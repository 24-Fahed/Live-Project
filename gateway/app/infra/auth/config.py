from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    JWT_SECRET: str = 'dev-secret-key'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRE_HOURS: int = 168

    AUTH_WHITELIST: list[str] = [
        '/api/wechat-login',
        '/api/v1/debate-topic',
        '/api/v1/ai-content',
        '/api/v1/comment',
        '/api/v1/like',
        '/health',
        '/admin',
        '/static',
        '/ws',
        '/docs',
        '/openapi.json',
        '/live'
    ]

    class Config:
        env_prefix = ''
        env_file = '.env'
        extra = 'ignore'


class WechatSettings(BaseSettings):
    WECHAT_APPID: str = ''
    WECHAT_SECRET: str = ''

    class Config:
        env_prefix = ''
        env_file = '.env'
        extra = 'ignore'


jwt_settings = JWTSettings()
wechat_settings = WechatSettings()
