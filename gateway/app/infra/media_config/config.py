"""Media-related infrastructure settings.

These settings belong to the media integration layer, not the business layer.
They mainly describe how the gateway talks to SRS and which push/play addresses
should be returned to callers in different environments.
"""

from pydantic_settings import BaseSettings

from app.infra.runtime.config import runtime_settings


class MediaSettings(BaseSettings):
    """Settings used by the gateway when integrating with the SRS media service."""

    # Docker service name or hostname of SRS in the current deployment.
    SRS_HOST: str = "srs"

    # RTMP ingest port used by OBS or other push clients.
    SRS_RTMP_PORT: int = 1935

    # HTTP port used by the gateway to read HLS files from SRS.
    SRS_HTTP_PORT: int = 8088

    # SRS application name. Current play URLs therefore become /live/live/*.m3u8.
    SRS_APP: str = "live"

    # External path prefix exposed by the gateway for HLS playback.
    SRS_PLAY_PATH_PREFIX: str = "/live"

    # Whether OBS is allowed to push directly to a public IP address.
    ALLOW_DIRECT_IP_PUSH: bool = True

    # Push base used in local Docker testing.
    LOCAL_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    # Push base used during staging/public integration testing.
    STAGING_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    # Push base used in the production environment.
    PRODUCTION_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    # Shared secret used when SRS sends callbacks back to the gateway.
    SRS_CALLBACK_TOKEN: str = "replace-me"

    # Reserved management token for protected media-admin operations.
    MEDIA_ADMIN_TOKEN: str = "replace-me"

    # Local fallback directory used when the gateway needs to rebuild an HLS
    # playlist from files that already exist on disk.
    SRS_FALLBACK_HLS_DIR: str = "/app/runtime/srs-html"

    # Number of recent segments to keep in the generated fallback playlist.
    SRS_FALLBACK_SEGMENT_WINDOW: int = 6

    # Target duration used when constructing the fallback playlist.
    SRS_FALLBACK_SEGMENT_DURATION: int = 5

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def http_upstream_base(self) -> str:
        """Base upstream URL used by the gateway to proxy SRS HTTP resources."""

        return f"http://{self.SRS_HOST}:{self.SRS_HTTP_PORT}"

    @property
    def play_path_prefix(self) -> str:
        """Normalize the configured play prefix into a single leading-slash path."""

        return "/" + self.SRS_PLAY_PATH_PREFIX.strip("/")

    @property
    def current_push_base(self) -> str:
        """Return the active RTMP push base for the current runtime.

        The runtime selection rule intentionally matches ``RuntimeSettings`` so
        users do not need to learn two different environment-switching models.
        """

        mode = (runtime_settings.APP_RUNTIME_MODE or runtime_settings.APP_ENV or "local").lower()
        if mode == "production":
            return self.PRODUCTION_PUSH_BASE.rstrip("/")
        if mode == "staging":
            return self.STAGING_PUSH_BASE.rstrip("/")
        return self.LOCAL_PUSH_BASE.rstrip("/")


media_settings = MediaSettings()
