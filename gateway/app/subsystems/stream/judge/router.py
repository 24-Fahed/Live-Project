from fastapi import APIRouter, Query

from app.subsystems.stream.judge.models import JudgesSaveRequest
from app.subsystems.stream.judge.service import judge_service

router = APIRouter()


@router.get("/admin/judges")
async def get_judges(stream_id: str = Query(..., alias="stream_id")):
    judges = judge_service.get_judges(stream_id)
    return {"success": True, "data": {"judges": judges}}


@router.post("/admin/judges")
async def save_judges(req: JudgesSaveRequest):
    judges = await judge_service.save_judges(req.stream_id, [j.model_dump() for j in req.judges])
    return {"success": True, "data": {"judges": judges}, "message": "评委信息保存成功"}
