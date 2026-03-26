# 微信登录子系统

## 设计模式

路由-服务两层架构（Router-Service）。无仓库层，不管理持久数据。

## 构件

| 文件 | 职责 |
|------|------|
| `models.py` | Pydantic 数据模型：登录请求结构 |
| `service.py` | `WechatLoginService`：mock 登录、调用 JWT `sign_token()` |
| `router.py` | `wechat_router`：API 路由定义 |

## 接口

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/api/wechat-login` | 微信登录 | 白名单（无需Token） |

## 请求/响应

```
POST /api/wechat-login
{"code": "wx_code_xxx", "userInfo": {"nickName": "用户", "avatarUrl": "http://..."}}

→ {"success": true, "data": {"token": "eyJhbGci...", "userInfo": {"nickName": "用户", "avatarUrl": "http://..."}}}
```

## 子系统集成

登录子系统调用 JWT 鉴权子系统的 `sign_token()` 生成 Token：

```python
from app.infra.auth import sign_token

token = sign_token({"openid": "mock-openid-xxx", "nickName": "用户", "avatarUrl": "..."})
```

登录 API 在 JWT 白名单中，不被中间件拦截。

## Mock 说明

原型阶段不调用微信 `jscode2session` API，直接生成 mock openid。生产环境需替换 `service.py` 中的登录逻辑。
