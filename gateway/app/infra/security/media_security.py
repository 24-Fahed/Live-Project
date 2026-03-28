from fastapi import HTTPException, Request

from app.infra.media_config.config import media_settings


async def verify_media_callback(request: Request) -> None:
    token = request.query_params.get("token") or request.headers.get("x-media-token")
    if token != media_settings.SRS_CALLBACK_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid media callback token")
