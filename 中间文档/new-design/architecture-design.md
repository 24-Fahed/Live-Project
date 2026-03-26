# 网关架构设计文档

> 版本: v1.0
> 日期: 2026-03-24
> 技术栈: Python + FastAPI

## 1. 设计概述

### 1.1 设计目标

将原单体网关（3635行 Node.js）重构为**微服务架构下的 API 网关**，实现：

| 目标 | 说明 |
|------|------|
| 请求路由 | 根据不同 API 路径，将请求转发到对应的后端微服务 |
| 统一鉴权 | 网关层统一处理 JWT 鉴权，只有通过鉴权的请求才能转发 |
| WebSocket 推送 | 支持实时数据推送，通过事件驱动机制响应后端服务的数据变更 |
| 静态资源 | 托管管理后台页面、HLS 流媒体文件 |
| 服务无关 | 网关不关心具体业务逻辑，任何微服务都能接入 |

### 1.2 核心设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 技术栈 | Python + FastAPI | 与后端微服务统一技术栈；FastAPI 原生支持 async/await 和 WebSocket |
| WebSocket 部署 | 一体化部署 | 系统规模不需要独立扩展；一体化架构运维更简单 |
| 事件驱动 | Redis Pub/Sub (Mock) | 轻量级、低延迟；适合实时推送场景；Mock 实现便于开发测试 |
| 鉴权方式 | JWT | 与原系统兼容；无状态，适合微服务架构 |

---

## 2. 系统架构图

### 2.1 整体架构（UML 组件图）

```mermaid
graph TB
    subgraph Clients["客户端"]
        MiniApp["微信小程序"]
        AdminPanel["管理后台"]
    end

    subgraph Gateway["API 网关 (Python + FastAPI)"]
        subgraph Core["核心组件"]
            Router["路由层<br/>APIRouter"]
            AuthMW["鉴权中间件<br/>JWT验证"]
            Proxy["请求转发<br/>httpx async"]
            WSHandler["WebSocket处理器<br/>room管理"]
        end

        subgraph EventSystem["事件系统"]
            EventBus["事件总线<br/>(Redis Mock)"]
            EventHandler["事件处理器"]
        end

        subgraph Static["静态资源"]
            AdminStatic["管理后台文件"]
            HLSFiles["HLS 流媒体"]
        end

        Config["配置模块"]
        Logger["日志模块"]
    end

    subgraph MessageBroker["消息代理 (Mock)"]
        RedisMock["Redis Pub/Sub Mock<br/>内存实现"]
    end

    subgraph Microservices["后端微服务"]
        VoteSvc["投票服务<br/>:8001"]
        StreamSvc["直播流服务<br/>:8002"]
        AISvc["AI内容服务<br/>:8003"]
        UserSvc["用户服务<br/>:8004"]
        OtherSvc["其他服务<br/>:8xxx"]
    end

    %% 客户端连接
    MiniApp -->|"HTTP + WebSocket"| Router
    AdminPanel -->|"HTTP"| Router

    %% 网关内部流程
    Router --> AuthMW
    AuthMW --> Proxy
    AuthMW --> WSHandler
    Proxy --> Microservices

    %% WebSocket 事件流
    WSHandler --> EventBus
    EventBus --> EventHandler
    EventHandler --> WSHandler

    %% 微服务事件发布
    Microservices -->|"发布事件"| RedisMock
    RedisMock -->|"订阅"| EventBus

    %% 静态资源
    Router --> Static

    %% 配置和日志
    Config --> Core
    Logger --> Core
```

### 2.2 请求处理流程（UML 活动图）

```mermaid
flowchart TD
    Start([请求到达网关]) --> CheckPath{路径判断}

    CheckPath -->|"/ws"| WSConnect[WebSocket连接]
    CheckPath -->|"/admin/*"| StaticFile[返回静态文件]
    CheckPath -->|"/hls/*"| HLSFile[返回HLS文件]
    CheckPath -->|"/api/*"| APIRequest[API请求处理]

    WSConnect --> WSSubscribe[订阅房间]
    WSSubscribe --> WSListen[监听消息/事件]

    APIRequest --> CheckAuth{需要鉴权?}
    CheckAuth -->|是| ValidateJWT[验证JWT Token]
    CheckAuth -->|否| RouteRequest

    ValidateJWT --> AuthResult{验证通过?}
    AuthResult -->|否| Return401[返回401 Unauthorized]
    AuthResult -->|是| RouteRequest[路由到目标服务]

    RouteRequest --> ForwardRequest[转发HTTP请求]
    ForwardRequest --> ServiceResponse[收到服务响应]
    ServiceResponse --> ReturnResponse[返回响应给客户端]

    %% WebSocket 事件推送流程
    subgraph EventFlow["事件驱动推送"]
        ServiceUpdate[微服务更新数据] --> PublishEvent[发布事件到Redis]
        PublishEvent --> EventReceived[网关接收事件]
        EventReceived --> WSBroadcast[广播到对应房间]
    end

    WSListen -.->|事件触发| WSBroadcast
```

---

## 3. 事件驱动架构设计

### 3.1 问题：微服务下如何触发 WebSocket 推送？

**旧架构**：投票 API 在网关中实现，投票后直接调用 `broadcast()` 推送。

**新架构**：投票逻辑在独立的投票服务中，网关不知道何时应该推送。

**解决方案**：**事件驱动架构** + **发布/订阅模式**

### 3.2 事件流程（UML 序列图）

```mermaid
sequenceDiagram
    participant Client as 小程序客户端
    participant Gateway as API网关
    participant VoteSvc as 投票服务
    participant EventBus as 事件总线<br/>(Redis Mock)
    participant WSClients as 其他WebSocket客户端

    Note over Client, WSClients: 用户投票场景

    Client->>Gateway: POST /api/v1/user-vote
    Gateway->>Gateway: 验证JWT Token
    Gateway->>VoteSvc: 转发请求到投票服务
    VoteSvc->>VoteSvc: 处理投票逻辑<br/>更新票数
    VoteSvc->>EventBus: 发布 "votes-updated" 事件<br/>{streamId, leftVotes, rightVotes}
    VoteSvc-->>Gateway: 返回投票结果
    Gateway-->>Client: 返回成功响应

    Note over EventBus, WSClients: 异步推送流程

    EventBus-->>Gateway: 订阅收到事件
    Gateway->>Gateway: 根据streamId找到对应房间
    Gateway->>WSClients: WebSocket广播<br/>{type: "votes-updated", data: {...}}
```

### 3.3 事件类型定义

| 事件类型 | 发布者 | 订阅者 | 数据结构 |
|---------|-------|-------|---------|
| `votes-updated` | 投票服务 | 网关 | `{streamId, leftVotes, rightVotes, totalVotes}` |
| `live-status-changed` | 直播流服务 | 网关 | `{streamId, isLive, streamUrl}` |
| `ai-status-changed` | AI服务 | 网关 | `{streamId, status}` |
| `new-ai-content` | AI服务 | 网关 | `{streamId, content}` |
| `debate-updated` | 辩题服务 | 网关 | `{streamId, debate}` |

### 3.4 Redis Mock 实现

```python
# 事件总线 Mock 实现（开发/测试环境使用）
class EventBusMock:
    """内存实现的发布/订阅，模拟 Redis Pub/Sub"""

    def __init__(self):
        self._channels: dict[str, list[Callable]] = {}
        self._messages: asyncio.Queue = asyncio.Queue()

    async def publish(self, channel: str, message: dict):
        """发布事件"""
        await self._messages.put((channel, message))

    async def subscribe(self, channel: str, handler: Callable):
        """订阅频道"""
        if channel not in self._channels:
            self._channels[channel] = []
        self._channels[channel].append(handler)

    async def start_listener(self):
        """启动事件监听循环"""
        while True:
            channel, message = await self._messages.get()
            if channel in self._channels:
                for handler in self._channels[channel]:
                    await handler(message)
```

---

## 4. 网关组件设计

### 4.1 组件图（UML 组件图）

```mermaid
graph LR
    subgraph Gateway["API 网关"]
        direction TB

        subgraph Layer1["接入层"]
            HTTP["HTTP 接入<br/>FastAPI"]
            WS["WebSocket 接入"]
        end

        subgraph Layer2["中间件层"]
            Auth["鉴权中间件"]
            Logger["日志中间件"]
            Cors["CORS 中间件"]
            RateLimit["限流中间件"]
        end

        subgraph Layer3["路由层"]
            APIRoutes["API 路由<br/>/api/*"]
            AdminRoutes["管理路由<br/>/admin/*"]
            StaticRoutes["静态路由<br/>/hls/*"]
        end

        subgraph Layer4["核心服务"]
            Proxy["请求代理"]
            RoomManager["房间管理器"]
            EventHub["事件中心"]
        end

        subgraph Layer5["基础设施"]
            Config["配置管理"]
            Logging["日志系统"]
            Health["健康检查"]
        end
    end

    Layer1 --> Layer2 --> Layer3 --> Layer4 --> Layer5
```

### 4.2 类图（UML 类图）

```mermaid
classDiagram
    class Gateway {
        -FastAPI app
        -Config config
        -RoomManager room_manager
        -EventBus event_bus
        +startup()
        +shutdown()
    }

    class RoomManager {
        -Dict~string, Room~ rooms
        +get_or_create_room(stream_id) Room
        +remove_room(stream_id)
        +add_client(stream_id, websocket)
        +remove_client(stream_id, websocket)
        +broadcast(stream_id, message)
        +broadcast_all(message)
    }

    class Room {
        +string stream_id
        +Set~WebSocket~ connections
        +datetime created_at
        +add_connection(ws)
        +remove_connection(ws)
        +broadcast(message)
    }

    class EventBus {
        <<interface>>
        +publish(channel, message)
        +subscribe(channel, handler)
        +unsubscribe(channel, handler)
    }

    class RedisEventBus {
        -Redis client
        +publish(channel, message)
        +subscribe(channel, handler)
    }

    class MockEventBus {
        -Dict channels
        -Queue messages
        +publish(channel, message)
        +subscribe(channel, handler)
    }

    class AuthMiddleware {
        -JWTConfig config
        -Set~string~ whitelist
        +verify_token(token) Payload
        +is_whitelisted(path) bool
    }

    class ProxyService {
        -Dict~string, str~ service_map
        -httpx.AsyncClient client
        +forward(request) Response
        +get_service_url(path) str
    }

    class Config {
        +int port
        +str host
        +Dict services
        +JWTConfig jwt
        +bool debug
        +from_env() Config
    }

    Gateway --> RoomManager
    Gateway --> EventBus
    Gateway --> AuthMiddleware
    Gateway --> ProxyService
    Gateway --> Config
    RoomManager --> Room
    EventBus <|.. RedisEventBus : 实现
    EventBus <|.. MockEventBus : 实现
```

---

## 5. 部署架构

### 5.1 部署图（UML 部署图）

```mermaid
graph TB
    subgraph Production["生产环境"]
        subgraph LoadBalancer["负载均衡"]
            Nginx["Nginx<br/>:80/:443"]
        end

        subgraph GatewayNode["网关节点"]
            GW1["Gateway Instance 1<br/>Python/FastAPI<br/>:8080"]
        end

        subgraph Services["微服务集群"]
            Vote["投票服务<br/>:8001"]
            Stream["直播流服务<br/>:8002"]
            AI["AI服务<br/>:8003"]
            User["用户服务<br/>:8004"]
        end

        subgraph MessageBroker["消息代理"]
            Redis["Redis<br/>:6379"]
        end

        subgraph Storage["存储"]
            DB["PostgreSQL/MySQL"]
            FileStorage["文件存储<br/>HLS/Admin"]
        end
    end

    Client["客户端"] --> Nginx
    Nginx --> GW1
    GW1 --> Vote
    GW1 --> Stream
    GW1 --> AI
    GW1 --> User
    GW1 <--> Redis
    Vote --> DB
    Stream --> DB
    AI --> DB
    User --> DB
    GW1 --> FileStorage
```

### 5.2 开发环境部署

```mermaid
graph LR
    subgraph Dev["开发环境"]
        GW["Gateway<br/>:8080"]
        MockEventBus["Mock EventBus<br/>(内存)"]
        MockServices["Mock Services<br/>:8001-8004"]
    end

    Client["小程序/后台"] --> GW
    GW <--> MockEventBus
    GW --> MockServices
```

---

## 6. API 路由设计

### 6.1 路由表

| 前缀 | 处理方式 | 目标服务 | 鉴权 |
|------|---------|---------|------|
| `/ws` | WebSocket 本地处理 | - | 可选 |
| `/admin/*` | 静态文件服务 | - | 否 |
| `/hls/*` | 静态文件服务 | - | 否 |
| `/api/v1/user-vote` | 转发 | 投票服务:8001 | 是 |
| `/api/v1/votes` | 转发 | 投票服务:8001 | 是 |
| `/api/v1/admin/streams` | 转发 | 直播流服务:8002 | 否 |
| `/api/v1/admin/ai-content` | 转发 | AI服务:8003 | 否 |
| `/api/v1/admin/users` | 转发 | 用户服务:8004 | 否 |
| `/api/v1/*` | 转发（通配） | 配置的服务 | 按白名单 |
| `/api/wechat-login` | 转发 | 用户服务:8004 | 否 |
| `/health` | 本地处理 | - | 否 |

### 6.2 服务发现配置

```yaml
# config/services.yaml
services:
  vote:
    url: http://localhost:8001
    routes:
      - /api/v1/votes
      - /api/v1/user-vote
      - /api/v1/user-votes
      - /api/v1/admin/votes

  stream:
    url: http://localhost:8002
    routes:
      - /api/v1/admin/streams
      - /api/v1/admin/live
      - /api/v1/admin/rtmp

  ai:
    url: http://localhost:8003
    routes:
      - /api/v1/ai-content
      - /api/v1/admin/ai-content
      - /api/v1/admin/ai

  user:
    url: http://localhost:8004
    routes:
      - /api/v1/users
      - /api/v1/admin/users
      - /api/wechat-login

  default:
    url: http://localhost:8000
```

---

## 7. 鉴权设计

### 7.1 鉴权流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Gateway as 网关
    participant AuthMW as 鉴权中间件
    participant Service as 后端服务

    Client->>Gateway: 请求 /api/v1/user-vote<br/>Header: Authorization: Bearer xxx

    Gateway->>AuthMW: 进入中间件

    AuthMW->>AuthMW: 检查路径是否在白名单

    alt 在白名单
        AuthMW->>Service: 直接转发
    else 不在白名单
        AuthMW->>AuthMW: 提取 Bearer Token
        AuthMW->>AuthMW: 验证 JWT 签名和有效期

        alt 验证失败
            AuthMW-->>Client: 401 Unauthorized
        else 验证成功
            AuthMW->>AuthMW: 解析用户信息到 request.state.user
            AuthMW->>Service: 转发请求（携带用户信息）
            Service-->>Gateway: 返回响应
            Gateway-->>Client: 返回响应
        end
    end
```

### 7.2 鉴权白名单

```python
# 不需要鉴权的路径
AUTH_WHITELIST = {
    "/api/wechat-login",
    "/api/v1/wechat-login",
    "/health",
    "/admin",
    "/hls",
    "/ws",
    "/api/v1/admin/streams",      # 管理后台API，后续通过IP白名单控制
    "/api/v1/admin/live",
    "/api/v1/admin/ai-content",
    "/api/v1/admin/ai",
    "/api/v1/admin/dashboard",
}
```

---

## 8. WebSocket 设计

### 8.1 房间管理

```mermaid
stateDiagram-v2
    [*] --> Connecting: 客户端连接
    Connecting --> Subscribed: 发送streamId
    Connecting --> DefaultRoom: 无streamId

    Subscribed --> InRoom: 加入房间
    DefaultRoom --> InRoom: 加入default房间

    InRoom --> Receiving: 接收消息
    Receiving --> InRoom: 继续监听

    InRoom --> Disconnecting: 客户端断开
    Disconnecting --> [*]

    note right of InRoom
        房间内广播：
        - votes-updated
        - live-status-changed
        - new-ai-content
        - debate-updated
    end note
```

### 8.2 WebSocket 消息协议

**客户端 → 服务端**

```json
{
    "type": "subscribe",
    "streamId": "stream-001"
}
```

**服务端 → 客户端**

```json
{
    "type": "connected",
    "message": "已连接到实时数据服务",
    "streamId": "stream-001"
}
```

```json
{
    "type": "votes-updated",
    "data": {
        "streamId": "stream-001",
        "leftVotes": 100,
        "rightVotes": 200,
        "leftPercentage": 33,
        "rightPercentage": 67,
        "totalVotes": 300
    },
    "timestamp": 1711267200000
}
```

---

## 9. 技术选型

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| Web 框架 | FastAPI | ^0.100 | 高性能异步框架 |
| HTTP 客户端 | httpx | ^0.25 | 异步 HTTP 客户端，用于转发请求 |
| WebSocket | websockets | ^12.0 | 或使用 FastAPI 原生 WebSocket |
| JWT | python-jose | ^3.3 | JWT 编解码 |
| 配置管理 | pydantic-settings | ^2.0 | 类型安全的配置 |
| 日志 | loguru | ^0.7 | 结构化日志 |
| Redis 客户端 | redis | ^5.0 | 生产环境使用 |
| ASGI 服务器 | uvicorn | ^0.24 | 高性能 ASGI 服务器 |

---

## 10. 与旧架构对比

| 维度 | 旧架构 (Node.js) | 新架构 (Python + FastAPI) |
|------|-----------------|--------------------------|
| 代码行数 | 3635 行单体文件 | 模块化，每个文件 < 300 行 |
| 业务逻辑 | 网关内实现 | 转发到微服务 |
| 数据存储 | 网关内 JSON 文件 | 微服务独立数据库 |
| WebSocket 推送 | 直接调用 broadcast() | 事件驱动，订阅发布模式 |
| 鉴权 | 网关内 JWT 验证 | 网关内 JWT 验证（相同） |
| 静态资源 | 网关内托管 | 网关内托管（相同） |
| 扩展性 | 单体难以扩展 | 水平扩展微服务 |
| 日志 | 111 处 console.log | 结构化日志系统 |
