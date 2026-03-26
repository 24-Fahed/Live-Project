# 直播子系统

## 架构

模块化单体架构。子系统内部按业务域拆分为独立模块，共享统一数据层。

```
stream/
├── __init__.py          # 聚合所有模块 router，对外暴露 stream_router
├── repository/          # 数据层
│   ├── __init__.py      # 实现切换（mock → mysql）
│   └── mock.py          # MockRepository：内存数据存储 + CRUD
├── live/                # 直播管理模块
├── vote/                # 投票管理模块
├── debate/              # 辩题管理模块
├── user/                # 用户管理模块
└── dashboard/           # 数据聚合模块
```

### 模块职责

| 模块 | 职责 | 内部组件 |
|------|------|---------|
| `repository/` | 数据存储，原型阶段使用内存字典 | `mock.py` |
| `live/` | 流配置 CRUD、开始/停止直播 | models, service, router |
| `vote/` | 投票读写、百分比计算 | models, service, router |
| `debate/` | 辩题 CRUD、流-辩题关联 | models, service, router |
| `user/` | 用户列表、在线状态查询 | service, router |
| `dashboard/` | 聚合多模块数据供 admin 面板使用 | service, router |

### 数据层设计

`repository/__init__.py` 导出 `repository` 实例，所有业务模块统一导入：

```python
from app.subsystems.stream.repository import repository
```

未来替换为 MySQL 时，只需修改 `__init__.py` 的导入，业务模块零改动。

### 模块间协作

- `dashboard` 模块从 `live`、`vote`、`debate` 模块读取数据聚合
- 所有模块共享 `ws_manager`（WebSocket 广播）和 `logger`（日志）
- 模块间通过导入彼此的 service 实例协作，不对外暴露

## API 端点

### 流管理（live 模块）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/streams` | 流列表 |
| POST | `/api/v1/admin/streams` | 创建流 |
| PUT | `/api/v1/admin/streams/{id}` | 更新流 |
| DELETE | `/api/v1/admin/streams/{id}` | 删除流 |

### 直播控制（live 模块）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/live/start` | 开始直播 |
| POST | `/api/v1/admin/live/stop` | 停止直播 |
| GET | `/api/v1/admin/live/status` | 直播状态 |
| POST | `/api/v1/admin/live/broadcast-viewers` | 广播观众数 |

### 辩题管理（debate 模块）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/debates` | 创建辩题 |
| GET | `/api/v1/admin/debates/{id}` | 获取辩题 |
| PUT | `/api/v1/admin/debates/{id}` | 更新辩题 |
| GET | `/api/v1/admin/streams/{id}/debate` | 获取流关联辩题 |
| PUT | `/api/v1/admin/streams/{id}/debate` | 关联辩题 |
| DELETE | `/api/v1/admin/streams/{id}/debate` | 解除关联 |
| GET | `/api/v1/debate-topic` | 公开接口：获取辩题 |

### 投票（vote 模块）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/votes` | 获取票数 |
| POST | `/api/v1/user-vote` | 用户投票 |
| GET | `/api/v1/admin/votes` | 管理员获取票数 |
| PUT | `/api/v1/admin/votes` | 管理员设置票数 |
| POST | `/api/v1/admin/votes/reset` | 重置票数 |
| POST | `/api/v1/admin/live/update-votes` | 直播面板更新票数 |
| POST | `/api/v1/admin/live/reset-votes` | 直播面板重置票数 |

### 用户管理（user 模块）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/users` | 用户列表（支持分页、搜索、状态过滤） |

查询参数：`page`、`pageSize`、`searchTerm`、`status`

#### 用户注册与在线状态

- **userId 标识**：系统使用微信 openid 作为 userId，贯穿登录、WebSocket 注册、用户管理全流程
- **注册**：用户首次微信登录时，wechat 子系统通过服务接口 `user_service.register_or_get_user()` 自动注册
- **资料更新**：已有用户再次登录时，同步更新昵称和头像
- **在线判断**：基于 WebSocket 连接状态实时判断，不依赖登录/登出事件

**数据流**：
```
微信登录 → 返回 userId(openid) → 前端存储到 localStorage
  → WebSocket 注册时携带 userId → ws_manager 追踪在线状态
  → user_service.list_users() 合并在线状态返回
```

### Dashboard（dashboard 模块）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/dashboard` | Dashboard 聚合数据 |
| GET | `/api/v1/admin/live/viewers` | 观众数 |

## 子系统间协作

| 协作方 | 接口 | 说明 |
|--------|------|------|
| wechat → stream.user | `user_service.register_or_get_user(user_id, nickname, avatar)` | 微信登录时注册或更新用户 |
| dashboard → live/vote/debate | 各模块 service 方法 | Dashboard 聚合多模块数据 |
| 所有模块 → ws_manager | `broadcast()` | WebSocket 广播 |
| user → ws_manager | `get_online_user_ids()` | 实时查询在线用户 |

## WebSocket 广播

| 事件 | 触发模块 | 数据 |
|------|---------|------|
| `liveStatus` | live | 直播状态变更 |
| `votes-updated` | vote | 票数变更 |
| `debate-updated` | debate | 辩题变更 |

## 未来扩展

新增业务模块只需：
1. 在 `stream/` 下新建目录（如 `judge/`、`ai_content/`、`statistics/`）
2. 实现 models/service/router
3. 在 `repository/mock.py` 添加对应数据和方法
4. 在 `stream/__init__.py` 注册 router
