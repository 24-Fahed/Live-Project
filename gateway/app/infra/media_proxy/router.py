from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from app.infra.media_config.config import media_settings
from app.infra.media_proxy.config import build_media_upstream_url

router = APIRouter(tags=["media-proxy"])


def _extract_segment_sequence(path: Path) -> int | None:
    try:
        return int(path.stem.rsplit("-", 1)[1])
    except (IndexError, ValueError):
        return None


def _build_fallback_playlist(upstream_path: str) -> str | None:
    playlist_path = Path(upstream_path.strip("/"))
    if playlist_path.suffix != ".m3u8":
        return None

    segment_dir = Path(media_settings.SRS_FALLBACK_HLS_DIR) / playlist_path.parent
    if not segment_dir.exists():
        return None

    stream_name = playlist_path.stem
    segments: list[tuple[int, Path]] = []
    for candidate in segment_dir.glob(f"{stream_name}-*.ts"):
        sequence = _extract_segment_sequence(candidate)
        if sequence is not None:
            segments.append((sequence, candidate))

    if not segments:
        return None

    segments.sort(key=lambda item: item[0])
    window = max(1, media_settings.SRS_FALLBACK_SEGMENT_WINDOW)
    recent_segments = segments[-window:]
    target_duration = max(1, media_settings.SRS_FALLBACK_SEGMENT_DURATION)
    media_sequence = recent_segments[0][0]

    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
        f"#EXT-X-TARGETDURATION:{target_duration}",
        f"#EXT-X-MEDIA-SEQUENCE:{media_sequence}",
    ]
    for _, segment_path in recent_segments:
        lines.append(f"#EXTINF:{target_duration:.3f},")
        lines.append(segment_path.name)
    lines.append("#EXT-X-ENDLIST")
    return "\n".join(lines) + "\n"


async def _proxy_to_upstream(upstream_path: str, request: Request) -> Response:
    upstream_url = build_media_upstream_url(upstream_path)
    headers = {}
    if request.headers.get("range"):
        headers["range"] = request.headers["range"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = await client.get(upstream_url, params=request.query_params, headers=headers)

    if upstream.status_code >= 400:
        if upstream.status_code == 404 and upstream_path.endswith(".m3u8"):
            fallback_playlist = _build_fallback_playlist(upstream_path)
            if fallback_playlist:
                return Response(
                    content=fallback_playlist,
                    status_code=200,
                    headers={"cache-control": "no-store"},
                    media_type="application/vnd.apple.mpegurl",
                )
        raise HTTPException(status_code=upstream.status_code, detail="Failed to fetch media from upstream")

    response_headers = {}
    for key in ("content-type", "accept-ranges", "content-range", "cache-control"):
        if key in upstream.headers:
            response_headers[key] = upstream.headers[key]

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


@router.get("/live/{media_path:path}")
async def proxy_live(media_path: str, request: Request):
    return await _proxy_to_upstream(f"live/{media_path}", request)
