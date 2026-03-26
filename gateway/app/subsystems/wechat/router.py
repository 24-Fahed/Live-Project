from fastapi import APIRouter

from app.subsystems.wechat.models import WechatLoginRequest
from app.subsystems.wechat.service import wechat_login_service

wechat_router = APIRouter()


@wechat_router.post("/wechat-login")
async def wechat_login(req: WechatLoginRequest):
    try:
        result = await wechat_login_service.login(req.code, req.userInfo)
        return {"success": True, "data": result}
    except ValueError as e:
        return {"success": False, "message": str(e)}
