from pydantic_settings import BaseSettings

from app.infra.runtime.config import runtime_settings


class EdgeSettings(BaseSettings):
    DOMAIN_ENABLED: bool = False
    HTTPS_ENABLED: bool = False
    CLOUDFLARE_ENABLED: bool = False
    USE_CLOUDFLARE_DNS: bool = False

    PUBLIC_DOMAIN: str = ""
    HTTP_PORT: int = 8080
    HTTPS_PORT: int = 443
    GATEWAY_PORT: int = 8080
    GATEWAY_INTERNAL_PORT: int = 8080
    GATEWAY_BIND_PORT: int = 8080
    GATEWAY_HOST: str = "0.0.0.0"

    TLS_CERT_FILE: str = "/app/certs/origin.crt"
    TLS_KEY_FILE: str = "/app/certs/origin.key"
    TLS_PROVIDER: str = "cloudflare-origin-ca"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def domain_enabled(self) -> bool:
        return bool(self.DOMAIN_ENABLED or runtime_settings.USE_DOMAIN)

    @property
    def cloudflare_enabled(self) -> bool:
        return bool(self.CLOUDFLARE_ENABLED or self.USE_CLOUDFLARE_DNS)

    @property
    def active_scheme(self) -> str:
        return "https" if self.HTTPS_ENABLED else "http"

    @property
    def active_port(self) -> int:
        return self.HTTPS_PORT if self.HTTPS_ENABLED else self.HTTP_PORT


edge_settings = EdgeSettings()
