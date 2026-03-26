from fastapi import APIRouter, Query

from app.subsystems.stream.vote.models import AdminVoteUpdate, ResetVoteRequest, UserVoteRequest
from app.subsystems.stream.vote.service import vote_service

router = APIRouter()


# ---- 用户投票 ----


@router.get("/votes")
async def get_votes(stream_id: str = Query("default", alias="stream_id")):
    return {"success": True, "data": vote_service.get_votes(stream_id)}


@router.post("/user-vote")
async def user_vote(req: UserVoteRequest):
    result = await vote_service.user_vote(req.streamId, req.leftVotes, req.rightVotes)
    return {"success": True, "data": result}


# ---- 管理员投票控制 ----


@router.get("/admin/votes")
async def admin_get_votes(stream_id: str = Query("default", alias="stream_id")):
    return {"success": True, "data": vote_service.get_votes(stream_id)}


@router.put("/admin/votes")
async def admin_set_votes(req: AdminVoteUpdate):
    result = await vote_service.admin_set_votes(req.streamId, req.leftVotes, req.rightVotes)
    return {"success": True, "data": result}


@router.post("/admin/votes/reset")
async def reset_votes(req: ResetVoteRequest):
    result = await vote_service.reset_votes(req.streamId)
    return {"success": True, "data": result, "message": "票数已重置"}


# ---- 直播面板投票控制（路径保持原样） ----


@router.post("/admin/live/update-votes")
async def admin_update_votes(req: AdminVoteUpdate):
    result = await vote_service.admin_update_votes(req.streamId, req.leftVotes, req.rightVotes, req.action)
    return {"success": True, "data": result, "message": "票数已更新"}


@router.post("/admin/live/reset-votes")
async def admin_reset_votes(req: ResetVoteRequest):
    result = await vote_service.reset_votes(req.streamId, req.resetTo, req.saveBackup)
    return {"success": True, "data": result, "message": "票数已重置"}
