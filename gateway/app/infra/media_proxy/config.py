"""媒体代理配置辅助函数。

该模块用于把网关对外暴露的媒体路径转换成 SRS 实际提供的上游地址。
"""

from app.infra.media_config.config import media_settings


# 网关对外通过 /live/... 暴露媒体资源，但底层文件实际来自 SRS 的 HTTP 服务。
def build_media_upstream_url(media_path: str) -> str:
    """构造网关媒体代理应访问的 SRS 上游地址。"""

    trimmed = media_path.lstrip("/")
    return f"{media_settings.http_upstream_base}/{trimmed}"
