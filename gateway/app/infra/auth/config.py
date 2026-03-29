"""Authentication and identity-related settings."""

from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    """JWT and gateway-auth related settings."""

    # Secret used to sign JWT tokens in development and deployment environments.
    JWT_SECRET: str = "dev-secret-key"

    # Signing algorithm used by the JWT helper.
    JWT_ALGORITHM: str = "HS256"

    # Token lifetime in hours.
    JWT_EXPIRE_HOURS: int = 168

    # Prefix-based whitelist. Requests matching these paths can pass through the
    # auth middleware without a JWT token. This list should stay short and should
    # only contain true public endpoints.
    AUTH_WHITELIST: list[str] = [
        "/api/wechat-login",
        "/api/v1/debate-topic",
        "/api/v1/ai-content",
        "/api/v1/comment",
        "/api/v1/like",
        "/health",
        "/admin",
        "/static",
        "/ws",
        "/docs",
        "/openapi.json",
        "/live",
    ]

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


class WechatSettings(BaseSettings):
    """Settings used by the WeChat login subsystem."""

    # WeChat mini program app ID.
    WECHAT_APPID: str = ""

    # WeChat mini program app secret.
    WECHAT_SECRET: str = ""

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


jwt_settings = JWTSettings()
wechat_settings = WechatSettings()
