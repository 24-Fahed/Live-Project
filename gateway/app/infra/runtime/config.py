"""Runtime-level settings used by the gateway infrastructure layer.

This module answers one very common question for readers:
"When the project needs to build an external URL, which base address does it use?"

The rule is intentionally simple:
1. If domain mode is enabled, prefer ``PUBLIC_BASE_URL``.
2. Otherwise choose a base URL by runtime mode.
3. If runtime mode is not configured, fall back to ``APP_ENV``.
4. If neither is configured, treat the process as ``local``.
"""

from pydantic_settings import BaseSettings


class RuntimeSettings(BaseSettings):
    """Settings that describe which deployment stage the gateway is running in.

    ``APP_ENV`` is the broad environment label, such as ``local`` / ``staging`` /
    ``production``.

    ``APP_RUNTIME_MODE`` is a more direct switch used by the gateway when it needs
    to decide which URL or behavior should be active right now. In the current
    project, it usually matches ``APP_ENV``. We still keep both fields because:

    - ``APP_ENV`` is familiar to most developers and deployment tools.
    - ``APP_RUNTIME_MODE`` makes it explicit that the gateway is choosing a
      runtime behavior, not just storing a label.

    If ``APP_RUNTIME_MODE`` is empty, the code falls back to ``APP_ENV`` so the
    project can still work with simpler environment files.
    """

    # Deployment stage label. Typical values are: local / staging / production.
    APP_ENV: str = "local"

    # Runtime behavior selector. When present, it takes priority over APP_ENV.
    APP_RUNTIME_MODE: str = "local"

    # When true, user-facing URLs should prefer the configured domain address.
    USE_DOMAIN: bool = False

    # Alias switch kept for clearer environment files in v0.1.2.
    DOMAIN_ENABLED: bool = False

    # When true, the current deployment is expected to work with a public IP.
    USE_PUBLIC_IP: bool = False

    # Base URL used by local development and local Docker testing.
    LOCAL_BASE_URL: str = "http://127.0.0.1:8080"

    # Base URL used during staging/public integration testing.
    STAGING_BASE_URL: str = "http://127.0.0.1:8080"

    # Public base URL used when the system exposes a domain or production entry.
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8080"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def domain_enabled(self) -> bool:
        """Return the effective domain switch used by the gateway."""

        return bool(self.DOMAIN_ENABLED or self.USE_DOMAIN)

    @property
    def current_base_url(self) -> str:
        """Return the active external base URL for the current gateway process.

        Why does this property check ``APP_RUNTIME_MODE`` first?
        Because the gateway needs one effective mode to decide which external
        address should be returned to Admin, the mini program, and media-related
        APIs. ``APP_RUNTIME_MODE`` is that effective mode.

        The fallback chain is:
        - ``APP_RUNTIME_MODE``
        - ``APP_ENV``
        - ``local``

        ``local`` means: no special staging or production behavior is active, so
        use the local development address.
        """

        mode = (self.APP_RUNTIME_MODE or self.APP_ENV or "local").lower()

        # Domain mode is a higher-level switch than the runtime label. Once the
        # system is told to use a domain, all externally returned URLs should use
        # PUBLIC_BASE_URL directly.
        if self.domain_enabled:
            return self.PUBLIC_BASE_URL.rstrip("/")

        # Production returns the final external entry address.
        if mode == "production":
            return self.PUBLIC_BASE_URL.rstrip("/")

        # Staging returns the staging/public-integration address.
        if mode == "staging":
            return self.STAGING_BASE_URL.rstrip("/")

        # Everything else falls back to the local development address.
        return self.LOCAL_BASE_URL.rstrip("/")

    @property
    def current_ws_base_url(self) -> str:
        """Return the active WebSocket base URL derived from ``current_base_url``."""

        base_url = self.current_base_url
        if base_url.startswith("https://"):
            return "wss://" + base_url[len("https://"):]
        if base_url.startswith("http://"):
            return "ws://" + base_url[len("http://"):]
        return base_url


runtime_settings = RuntimeSettings()
