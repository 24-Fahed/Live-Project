from pydantic_settings import BaseSettings


class EdgeSettings(BaseSettings):
    PUBLIC_DOMAIN: str = ""
    GATEWAY_PORT: int = 8080
    USE_CLOUDFLARE_DNS: bool = False

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


edge_settings = EdgeSettings()
