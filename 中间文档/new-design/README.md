# 直播辩论系统 - 微服务 API 网关

> 技术栈: Python + FastAPI
> 版本: v2.0.0 (重构版)

## 项目概述

本网关是直播辩论系统的核心入口，采用微服务架构设计，负责：

- **请求路由**: 根据路径将 API 请求转发到对应的后端微服务
- **统一鉴权**: JWT Token 验证，保护需要认证的 API
- **WebSocket 推送**: 实时数据推送，支持多房间隔离
- **静态资源**: 管理后台页面和 HLS 流媒体服务

## 设计文档

| 文档 | 说明 |
|------|------|
| [architecture-design.md](./architecture-design.md) | 系统架构设计（UML 图） |
| [project-structure.md](./project-structure.md) | 项目目录结构和核心代码示例 |
| [event-driven-design.md](./event-driven-design.md) | 事件驱动架构设计（解决微服务 WebSocket 推送问题） |

## 架构概览

```
┌─────────────┐     ┌─────────────────────────────────────────────┐
│  微信小程序  │────▶│                                             │
├─────────────┤     │              API 网关 (Python)               │
│  管理后台    │────▶│  ┌─────────┬─────────┬─────────┬─────────┐ │
└─────────────┘     │  │ 路由层  │ 中间件  │ WebSocket│ 事件系统 │ │
                    │  └────┬────┴────┬────┴────┬────┴────┬────┘ │
                    └───────┼─────────┼─────────┼─────────┼──────┘
                            │         │         │         │
                            ▼         ▼         ▼         ▼
                    ┌───────────┐ ┌───────────┐ ┌───────────┐
                    │ 投票服务   │ │ 直播流服务 │ │ AI服务... │
                    │ :8001     │ │ :8002     │ │ :8003     │
                    └───────────┘ └───────────┘ └───────────┘
```

## 核心设计决策

### 1. 事件驱动解决 WebSocket 推送

**问题**: 微服务架构下，投票逻辑在独立的投票服务中，网关不知道何时应该推送。

**方案**: 发布/订阅模式

```
用户投票 → 投票服务处理 → 发布事件 → 网关订阅 → WebSocket 广播
```

详见 [event-driven-design.md](./event-driven-design.md)

### 2. 鉴权设计

- 网关统一验证 JWT Token
- 白名单机制：登录接口、管理后台等不需要鉴权
- 用户信息透传：验证通过后，通过 Header 传递给后端服务

### 3. 服务发现

通过配置文件定义路由规则：

```yaml
services:
  vote:
    url: http://localhost:8001
    routes:
      - /api/v1/votes
      - /api/v1/user-vote
```

## 与旧架构对比

| 维度 | 旧架构 (Node.js 单体) | 新架构 (Python 微服务) |
|------|---------------------|----------------------|
| 代码量 | 3635 行单文件 | 模块化，每文件 < 300 行 |
| 业务逻辑 | 网关内实现 | 转发到微服务 |
| WebSocket 触发 | 直接调用 | 事件驱动 |
| 数据存储 | JSON 文件 | 微服务独立数据库 |
| 扩展性 | 单体难扩展 | 水平扩展微服务 |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 开发模式（使用 Mock 事件总线）
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8080

# 生产模式（使用 Redis）
# 修改 .env: USE_REDIS=true
docker-compose up -d redis
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 环境变量

```bash
# 应用配置
PORT=8080
DEBUG=false

# JWT 配置
JWT_SECRET=your-secret-key

# Redis 配置
USE_REDIS=false
REDIS_URL=redis://localhost:6379
```

## 目录结构

```
live-gateway/
├── app/
│   ├── main.py              # 入口
│   ├── core/                # 配置、安全
│   ├── middleware/          # 中间件
│   ├── api/                 # 路由
│   ├── websocket/           # WebSocket
│   ├── events/              # 事件系统
│   └── services/            # 服务客户端
├── static/                  # 静态资源
├── config/                  # 配置文件
├── tests/                   # 测试
└── docs/                    # 文档
```

## 相关链接

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Redis Pub/Sub](https://redis.io/docs/manual/pubsub/)
- [UML 2.0 标准](https://www.omg.org/spec/UML/2.5/)
