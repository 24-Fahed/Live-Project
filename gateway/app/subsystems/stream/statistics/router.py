from fastapi import APIRouter, Query

from app.subsystems.stream.statistics.service import statistics_service

router = APIRouter()


@router.get("/admin/statistics/votes")
async def get_votes_statistics(
    stream_id: str = "default",
    time_range: str = Query("1h", pattern="^(1h|6h|12h|24h|7d)$"),
):
    data = statistics_service.get_votes_timeline(stream_id, time_range)
    return {"success": True, "data": data}
