from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger


class UserService:
    def register_or_get_user(self, user_id: str, nickname: str = "", avatar: str = "") -> dict:
        """注册或获取用户。供外部子系统（如微信登录）调用。"""
        is_new = repository.get_user(user_id) is None
        user = repository.get_or_create_user(user_id, nickname, avatar)
        if is_new:
            logger.info("User registered", extra={"module": "stream", "user_id": user_id})
        return user

    def list_users(self, page: int = 1, page_size: int = 20, search_term: str = "", status: str = "") -> dict:
        users = repository.list_users()

        # 获取在线用户 ID
        online_ids = ws_manager.get_online_user_ids()

        # 附加在线状态
        for user in users:
            user["status"] = "online" if user["userId"] in online_ids else "offline"

        # 搜索过滤
        if search_term:
            term = search_term.lower()
            users = [u for u in users if term in u.get("nickname", "").lower() or term in u.get("userId", "").lower()]

        # 状态过滤
        if status:
            users = [u for u in users if u["status"] == status]

        # 分页
        total = len(users)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = users[start:end]

        return {
            "users": paginated,
            "total": total,
            "page": page,
            "pageSize": page_size,
        }


user_service = UserService()
