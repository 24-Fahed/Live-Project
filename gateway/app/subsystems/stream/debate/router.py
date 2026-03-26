from fastapi import APIRouter

from app.subsystems.stream.debate.models import DebateCreate, DebateUpdate
from app.subsystems.stream.debate.service import debate_service

router = APIRouter()


# ---- 辩题管理 ----


@router.post("/admin/debates")
async def create_debate(req: DebateCreate):
    debate = await debate_service.create_debate(
        req.title, req.description, req.leftPosition, req.rightPosition, req.isActive
    )
    return {"success": True, "data": debate, "message": "辩题创建成功"}


@router.get("/admin/debates/{debate_id}")
async def get_debate(debate_id: str):
    debate = debate_service.get_debate_by_id(debate_id)
    if not debate:
        return {"success": False, "message": "辩题不存在"}
    return {"success": True, "data": debate}


@router.put("/admin/debates/{debate_id}")
async def update_debate(debate_id: str, req: DebateUpdate):
    debate = await debate_service.update_debate(debate_id, **req.model_dump(exclude_none=True))
    if not debate:
        return {"success": False, "message": "辩题不存在"}
    return {"success": True, "data": debate, "message": "辩题更新成功"}


# ---- 流-辩题关联 ----


@router.get("/admin/streams/{stream_id}/debate")
async def get_stream_debate(stream_id: str):
    debate = debate_service.get_debate(stream_id)
    if not debate:
        return {"success": False, "message": "该流未关联辩题"}
    return {"success": True, "data": debate}


@router.put("/admin/streams/{stream_id}/debate")
async def associate_debate(stream_id: str, body: dict):
    debate_id = body.get("debate_id")
    if not debate_id:
        return {"success": False, "message": "缺少 debate_id"}
    ok = await debate_service.associate_debate(stream_id, debate_id)
    if not ok:
        return {"success": False, "message": "辩题不存在或关联失败"}
    return {"success": True, "message": "辩题关联成功"}


@router.delete("/admin/streams/{stream_id}/debate")
async def delete_stream_debate(stream_id: str):
    ok = await debate_service.remove_stream_debate(stream_id)
    if not ok:
        return {"success": False, "message": "该流未关联辩题"}
    return {"success": True, "message": "辩题已解除关联"}


# ---- 公开接口 ----


@router.get("/debate-topic")
async def get_debate_topic(stream_id: str = "default"):
    debate = debate_service.get_debate(stream_id)
    if not debate:
        return {"success": False, "message": "辩题不存在"}
    return {"success": True, "data": debate}
