"""Edge access settings for the gateway.

This module keeps settings that belong to the access edge of the system, for
example domain name, port selection, and TLS-related switches. These fields
explain how traffic reaches the gateway, not how business logic works.
"""

from pydantic_settings import BaseSettings

from app.infra.runtime.config import runtime_settings


class EdgeSettings(BaseSettings):
    """Settings for gateway exposure and access entry behavior."""

    # Whether the system should expose a domain-based entry in the current run.
    DOMAIN_ENABLED: bool = False

    # Whether the gateway should start with TLS enabled.
    HTTPS_ENABLED: bool = False

    # Whether the deployment expects Cloudflare to participate in the access path.
    CLOUDFLARE_ENABLED: bool = False

    # Kept for compatibility with earlier env files that only modeled DNS usage.
    USE_CLOUDFLARE_DNS: bool = False

    # Public domain used by external users, for example ``example.com``.
    PUBLIC_DOMAIN: str = ""

    # Conventional HTTP and HTTPS ports used in documentation and runtime checks.
    HTTP_PORT: int = 8080
    HTTPS_PORT: int = 443

    # Gateway port settings: compatibility field, internal container port, and
    # externally published host port.
    GATEWAY_PORT: int = 8080
    GATEWAY_INTERNAL_PORT: int = 8080
    GATEWAY_BIND_PORT: int = 8080
    GATEWAY_HOST: str = "0.0.0.0"

    # TLS certificate locations inside the gateway container.
    TLS_CERT_FILE: str = "/app/certs/origin.crt"
    TLS_KEY_FILE: str = "/app/certs/origin.key"
    TLS_PROVIDER: str = "cloudflare-origin-ca"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def domain_enabled(self) -> bool:
        """Return the effective domain switch used by the edge layer."""

        return bool(self.DOMAIN_ENABLED or runtime_settings.USE_DOMAIN)

    @property
    def cloudflare_enabled(self) -> bool:
        """Return whether Cloudflare behavior is effectively enabled."""

        return bool(self.CLOUDFLARE_ENABLED or self.USE_CLOUDFLARE_DNS)

    @property
    def active_scheme(self) -> str:
        """Return the effective scheme used by the current access edge."""

        return "https" if self.HTTPS_ENABLED else "http"

    @property
    def active_port(self) -> int:
        """Return the effective external port for the current edge scheme."""

        return self.HTTPS_PORT if self.HTTPS_ENABLED else self.HTTP_PORT


edge_settings = EdgeSettings()
