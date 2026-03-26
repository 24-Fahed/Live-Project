from fastapi import APIRouter, Query

from app.subsystems.stream.live.models import LiveStartRequest, LiveStopRequest, StreamCreate, StreamUpdate
from app.subsystems.stream.live.service import live_service

router = APIRouter()


# ---- 流管理 ----


@router.get("/admin/streams")
async def list_streams():
    return {"success": True, "data": live_service.list_streams()}


@router.post("/admin/streams")
async def create_stream(req: StreamCreate):
    stream = live_service.create_stream(req.name, req.url, req.type, req.description)
    return {"success": True, "data": stream, "message": "流创建成功"}


@router.put("/admin/streams/{stream_id}")
async def update_stream(stream_id: str, req: StreamUpdate):
    stream = live_service.update_stream(stream_id, **req.model_dump(exclude_none=True))
    if not stream:
        return {"success": False, "message": "流不存在"}
    return {"success": True, "data": stream}


@router.delete("/admin/streams/{stream_id}")
async def delete_stream(stream_id: str):
    stream = live_service.delete_stream(stream_id)
    if not stream:
        return {"success": False, "message": "流不存在"}
    return {"success": True, "data": {"id": stream["id"], "name": stream["name"]}, "message": "流已删除"}


# ---- 直播控制 ----


@router.post("/admin/live/start")
async def start_live(req: LiveStartRequest):
    status = await live_service.start_live(req.streamId)
    return {"success": True, "data": {**status, "status": "started"}, "message": "直播已开始"}


@router.post("/admin/live/stop")
async def stop_live(req: LiveStopRequest):
    result = await live_service.stop_live(req.streamId)
    return {"success": True, "data": {**result, "status": "stopped"}, "message": "直播已停止"}


@router.get("/admin/live/status")
async def get_live_status(stream_id: str = "default"):
    return {"success": True, "data": live_service.get_live_status(stream_id)}


@router.post("/admin/live/broadcast-viewers")
async def broadcast_viewers(stream_id: str = Query("default", alias="stream_id")):
    count = live_service.get_viewers_count(stream_id)
    return {"success": True, "data": {"streamId": stream_id, "count": count}}
