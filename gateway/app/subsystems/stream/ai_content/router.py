from fastapi import APIRouter, Query

from app.subsystems.stream.ai_content.models import (
    AIContentCreate,
    AIStartRequest,
    AIStopRequest,
    AIToggleRequest,
    CommentCreate,
    LikeCreate,
    CommentDelete,
)
from app.subsystems.stream.ai_content.service import ai_content_service

router = APIRouter()


# ---- 公开接口 ----


@router.get("/ai-content")
async def list_ai_content(stream_id: str = Query("default", alias="stream_id")):
    return {"success": True, "data": ai_content_service.list_contents(stream_id)}


@router.post("/comment")
async def add_comment(req: CommentCreate):
    """添加评论到 AI 内容。"""
    result = ai_content_service.add_comment(req.contentId, req.text, req.user, req.avatar)
    if not result:
        return {"success": False, "message": "内容不存在"}
    return {"success": True, "data": result, "message": "评论已添加"}


@router.delete("/comment/{comment_id}")
async def delete_comment(comment_id: str, req: CommentDelete):
    """删除评论。"""
    result = ai_content_service.delete_comment(req.contentId, comment_id)
    if not result:
        return {"success": False, "message": "评论或内容不存在"}
    return {"success": True, "data": result, "message": "评论已删除"}


@router.post("/like")
async def add_like(req: LikeCreate):
    """点赞 AI 内容或评论。"""
    result = ai_content_service.add_like(req.contentId, req.commentId)
    if not result:
        return {"success": False, "message": "内容或评论不存在"}
    return {"success": True, "data": result, "message": "点赞成功"}


# ---- 管理接口 ----


@router.get("/admin/ai-content/list")
async def list_ai_content_admin(
    page: int = Query(1),
    pageSize: int = Query(20),
    stream_id: str = Query(None, alias="stream_id"),
):
    return {"success": True, "data": ai_content_service.list_admin(page, pageSize, stream_id)}


@router.get("/admin/ai-content/{content_id}")
async def get_ai_content(content_id: str):
    item = ai_content_service.get_content(content_id)
    if not item:
        return {"success": False, "message": "内容不存在"}
    return {"success": True, "data": item}


@router.delete("/admin/ai-content/{content_id}")
async def delete_ai_content(content_id: str):
    item = ai_content_service.delete_content(content_id)
    if not item:
        return {"success": False, "message": "内容不存在"}
    return {"success": True, "data": item, "message": "内容已删除"}


@router.get("/admin/ai-content/{content_id}/comments")
async def list_ai_comments(content_id: str):
    comments = ai_content_service.list_comments(content_id)
    return {"success": True, "data": {"comments": comments}}


@router.delete("/admin/ai-content/{content_id}/comments/{comment_id}")
async def delete_ai_comment(content_id: str, comment_id: str):
    comment = ai_content_service.delete_comment(content_id, comment_id)
    if not comment:
        return {"success": False, "message": "评论不存在"}
    return {"success": True, "data": comment, "message": "评论已删除"}


# ---- AI 生命周期管理 ----


@router.post("/admin/ai/start")
async def start_ai(req: AIStartRequest):
    result = await ai_content_service.start(req.streamId, req.settings)
    return {"success": True, "data": result, "message": "AI识别已启动"}


@router.post("/admin/ai/stop")
async def stop_ai(req: AIStopRequest):
    result = await ai_content_service.stop(req.streamId)
    return {"success": True, "data": result, "message": "AI识别已停止"}


@router.post("/admin/ai/toggle")
async def toggle_ai(req: AIToggleRequest):
    result = await ai_content_service.toggle(req.streamId, req.action)
    if result is None:
        return {"success": False, "message": "操作失败"}
    return {"success": True, "data": result, "message": f"AI识别已{req.action}"}
