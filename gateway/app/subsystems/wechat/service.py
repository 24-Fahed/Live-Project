import httpx

from app.infra.auth import sign_token
from app.infra.auth.config import wechat_settings
from app.subsystems.stream.user.service import user_service
from app.utils.logger.logger import logger

_WECHAT_API = "https://api.weixin.qq.com/sns/jscode2session"


class WechatLoginService:
    async def login(self, code: str, user_info: dict | None) -> dict:
        openid, session_key = await self._jscode2session(code)

        if user_info:
            nick_name = user_info.get("nickName", "微信用户")
            avatar_url = user_info.get("avatarUrl", "")
        else:
            nick_name = "微信用户"
            avatar_url = ""

        token = sign_token({"openid": openid, "nickName": nick_name, "avatarUrl": avatar_url})

        # 注册或更新用户到直播子系统的用户管理
        user_service.register_or_get_user(openid, nick_name, avatar_url)

        logger.info("Wechat login", extra={"module": "wechat", "openid": openid})

        return {
            "token": token,
            "userId": openid,
            "userInfo": {"nickName": nick_name, "avatarUrl": avatar_url},
        }

    async def _jscode2session(self, code: str) -> tuple[str, str]:
        params = {
            "appid": wechat_settings.WECHAT_APPID,
            "secret": wechat_settings.WECHAT_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient(timeout=10.0, proxy=None) as client:
            resp = await client.get(_WECHAT_API, params=params)
            data = resp.json()

        if "openid" not in data:
            logger.error(f"Wechat jscode2session failed", extra={"module": "wechat", "response": data})
            raise ValueError(f"微信登录失败: {data.get('errmsg', 'unknown error')}")

        return data["openid"], data.get("session_key", "")


wechat_login_service = WechatLoginService()
