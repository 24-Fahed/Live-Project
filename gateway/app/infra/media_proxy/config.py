from app.infra.media_config.config import media_settings


def build_media_upstream_url(media_path: str) -> str:
    trimmed = media_path.lstrip("/")
    return f"{media_settings.http_upstream_base}/{trimmed}"
