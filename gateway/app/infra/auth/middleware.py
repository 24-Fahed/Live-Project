from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.infra.auth.config import jwt_settings
from app.infra.auth.token import verify_token
from app.utils.logger.logger import logger


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if self._is_whitelisted(path):
            return await call_next(request)

        if path.startswith("/api/v1/admin/"):
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        token = auth[7:]
        try:
            payload = verify_token(token)
            request.state.user = payload
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        return await call_next(request)

    @staticmethod
    def _is_whitelisted(path: str) -> bool:
        return any(path.startswith(p) for p in jwt_settings.AUTH_WHITELIST)
