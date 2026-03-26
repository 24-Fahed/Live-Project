# JWT 鉴权子系统

## 设计模式

中间件模式（Middleware）。子系统的身份由职责（Token 生命周期管理）决定，实现方式是 FastAPI 中间件。

## 构件

| 文件 | 职责 |
|------|------|
| `config.py` | JWT 配置：密钥、算法、过期时间、白名单 |
| `token.py` | `sign_token()` 生成 Token，`verify_token()` 验证 Token |
| `middleware.py` | `AuthMiddleware`：拦截请求、校验白名单、验证 Token、注入 `request.state.user` |

## 接口

| 接口 | 参数 | 调用者 | 说明 |
|------|------|--------|------|
| `sign_token(user_info)` | user_info: dict | 微信登录子系统 | 生成 JWT Token，返回字符串 |
| `verify_token(token)` | token: str | 中间件内部 | 验证 Token，返回 payload dict |
| `AuthMiddleware` | - | main.py | 注册为中间件，拦截请求验证 Token |

## 白名单

以下路径不需要 Token：

- `/api/wechat-login`
- `/health`
- `/admin`
- `/ws`
- `/docs`
- `/openapi.json`
- `/api/v1/admin/*`

## 配置

通过环境变量或 `.env` 文件覆盖：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `JWT_SECRET` | `dev-secret-key` | 签名密钥 |
| `JWT_ALGORITHM` | `HS256` | 算法 |
| `JWT_EXPIRE_HOURS` | `168` | Token 有效期（小时） |

## 接入方式

### 被调用方（微信登录子系统）

```python
from app.infra.auth import sign_token

token = sign_token({"openid": "xxx", "nickName": "用户"})
```

### 注册方（main.py）

```python
from app.infra.auth import AuthMiddleware
app.add_middleware(AuthMiddleware)
```

### 使用方（业务子系统）

中间件自动将用户信息注入 `request.state.user`，业务代码直接读取：

```python
def some_route(request: Request):
    user = request.state.user  # {"openid": "xxx", "nickName": "用户", ...}
```
