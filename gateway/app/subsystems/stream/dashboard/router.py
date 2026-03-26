from fastapi import APIRouter, Query

from app.subsystems.stream.dashboard.service import dashboard_service

router = APIRouter()


@router.get("/admin/dashboard")
async def get_dashboard(stream_id: str = "default"):
    return {"success": True, "data": dashboard_service.get_dashboard(stream_id)}


@router.get("/admin/live/viewers")
async def get_viewers(stream_id: str = Query(None)):
    if stream_id:
        return {"success": True, "data": {"streamId": stream_id, "count": dashboard_service.get_viewers_count(stream_id)}}
    return {"success": True, "data": dashboard_service.get_viewers()}
