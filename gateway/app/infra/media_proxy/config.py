"""Helpers for translating an external media path into an upstream SRS URL."""

from app.infra.media_config.config import media_settings


# The gateway exposes media resources through /live/... but actually fetches the
# underlying files from the SRS HTTP service.
def build_media_upstream_url(media_path: str) -> str:
    """Build the SRS upstream URL used by the gateway media proxy."""

    trimmed = media_path.lstrip("/")
    return f"{media_settings.http_upstream_base}/{trimmed}"
