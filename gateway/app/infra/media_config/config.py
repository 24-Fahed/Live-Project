from pydantic_settings import BaseSettings

from app.infra.runtime.config import runtime_settings


class MediaSettings(BaseSettings):
    SRS_HOST: str = "srs"
    SRS_RTMP_PORT: int = 1935
    SRS_HTTP_PORT: int = 8088
    SRS_APP: str = "live"
    SRS_PLAY_PATH_PREFIX: str = "/live"
    ALLOW_DIRECT_IP_PUSH: bool = True

    LOCAL_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"
    STAGING_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"
    PRODUCTION_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    SRS_CALLBACK_TOKEN: str = "replace-me"
    MEDIA_ADMIN_TOKEN: str = "replace-me"
    SRS_FALLBACK_HLS_DIR: str = "/app/runtime/srs-html"
    SRS_FALLBACK_SEGMENT_WINDOW: int = 6
    SRS_FALLBACK_SEGMENT_DURATION: int = 5

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def http_upstream_base(self) -> str:
        return f"http://{self.SRS_HOST}:{self.SRS_HTTP_PORT}"

    @property
    def play_path_prefix(self) -> str:
        return "/" + self.SRS_PLAY_PATH_PREFIX.strip("/")

    @property
    def current_push_base(self) -> str:
        mode = (runtime_settings.APP_RUNTIME_MODE or runtime_settings.APP_ENV or "local").lower()
        if mode == "production":
            return self.PRODUCTION_PUSH_BASE.rstrip("/")
        if mode == "staging":
            return self.STAGING_PUSH_BASE.rstrip("/")
        return self.LOCAL_PUSH_BASE.rstrip("/")


media_settings = MediaSettings()
