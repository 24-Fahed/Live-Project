"""认证与身份相关配置。"""

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    """JWT 与网关认证相关配置。"""

    # 开发与部署环境中用于签发 JWT 的密钥。
    JWT_SECRET: str = "change-me-in-production"

    # JWT 签名算法。
    JWT_ALGORITHM: str = "HS256"

    # Token 有效期，单位为小时。
    JWT_EXPIRE_HOURS: int = 24

    # 按路径前缀匹配的白名单。命中这些路径的请求可跳过 JWT 校验。
    # 这里应保持精简，只保留真正公开的入口。
    AUTH_WHITELIST: list[str] = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/admin",
        "/static",
        "/live",
        "/api/v1/wechat/login",
        "/api/v1/wechat/profile",
    ]

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


class WechatSettings(BaseSettings):
    """微信登录子系统使用的配置。"""

    # 微信小程序 AppID。
    WECHAT_APPID: str = ""

    # 微信小程序 AppSecret。
    WECHAT_SECRET: str = ""

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


jwt_settings = AuthSettings()
wechat_settings = WechatSettings()
