from fastapi import APIRouter, Request

from app.infra.security.media_security import verify_media_callback
from app.subsystems.media.service import media_service

media_router = APIRouter(tags=["media"])


@media_router.get("/admin/media/push-config")
async def get_push_config(stream_id: str = "stream-001"):
    return {"success": True, "data": media_service.get_stream_info(stream_id)}


@media_router.get("/admin/media/streams/{stream_id}")
async def get_media_stream_info(stream_id: str):
    return {"success": True, "data": media_service.get_stream_info(stream_id)}


@media_router.get("/media/play-url")
async def get_play_url(stream_id: str = "stream-001"):
    data = media_service.get_stream_info(stream_id)
    return {"success": True, "data": {"streamId": stream_id, "playUrl": data["playUrl"]}}


@media_router.post("/internal/media/hooks/{event_name}")
async def handle_media_hook(event_name: str, request: Request):
    await verify_media_callback(request)
    payload = await request.json()
    return {"success": True, "data": media_service.mark_event(event_name, payload)}
