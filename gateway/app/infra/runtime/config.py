from pydantic_settings import BaseSettings


class RuntimeSettings(BaseSettings):
    APP_ENV: str = "local"
    APP_RUNTIME_MODE: str = "local"
    USE_DOMAIN: bool = False
    USE_PUBLIC_IP: bool = False

    LOCAL_BASE_URL: str = "http://127.0.0.1:8080"
    STAGING_BASE_URL: str = "http://127.0.0.1:8080"
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8080"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def current_base_url(self) -> str:
        mode = (self.APP_RUNTIME_MODE or self.APP_ENV or "local").lower()
        if self.USE_DOMAIN:
            return self.PUBLIC_BASE_URL.rstrip("/")
        if mode == "production":
            return self.PUBLIC_BASE_URL.rstrip("/")
        if mode == "staging":
            return self.STAGING_BASE_URL.rstrip("/")
        return self.LOCAL_BASE_URL.rstrip("/")


runtime_settings = RuntimeSettings()
