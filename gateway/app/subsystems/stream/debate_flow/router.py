from fastapi import APIRouter, Query

from app.subsystems.stream.debate_flow.models import (
    DebateFlowControlRequest,
    DebateFlowSaveRequest,
)
from app.subsystems.stream.debate_flow.service import debate_flow_service

router = APIRouter()


@router.get("/admin/debate-flow")
async def get_debate_flow(stream_id: str = Query(..., alias="stream_id")):
    flow = debate_flow_service.get_flow(stream_id)
    return {"success": True, "data": flow}


@router.post("/admin/debate-flow")
async def save_debate_flow(req: DebateFlowSaveRequest):
    segments = await debate_flow_service.save_flow(
        req.stream_id, [s.model_dump() for s in req.segments]
    )
    return {"success": True, "data": {"segments": segments}, "message": "流程配置保存成功"}


@router.post("/admin/debate-flow/control")
async def control_debate_flow(req: DebateFlowControlRequest):
    state = await debate_flow_service.control_flow(req.stream_id, req.action)
    return {"success": True, "data": state, "message": f"流程控制: {req.action}"}
