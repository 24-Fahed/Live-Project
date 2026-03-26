from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.comm.ws.handler import handle_websocket
from app.infra.auth import AuthMiddleware
from app.infra.static import setup as setup_static
from app.subsystems.stream import stream_router
from app.subsystems.wechat import wechat_router
from app.utils.logger.logger import logger


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/admin/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app = FastAPI(title="Live Debate Gateway", version="3.0")

app.add_middleware(AuthMiddleware)
app.add_middleware(NoCacheMiddleware)
setup_static(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wechat_router, prefix="/api")
app.include_router(stream_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await handle_websocket(ws)
