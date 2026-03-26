import json

from fastapi import WebSocket, WebSocketDisconnect

from app.comm.ws.manager import ws_manager
from app.utils.logger.logger import logger


async def handle_websocket(ws: WebSocket):
    await ws_manager.connect(ws)

    await ws_manager.send(ws, {
        "type": "connected",
        "data": {"message": "已连接到实时数据服务"},
    })

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue

            msg_type = msg.get("type", "")

            if msg_type == "register":
                ws_manager.register(ws, msg)
                await ws_manager.send(ws, {
                    "type": "registered",
                    "data": {"message": "注册成功"},
                })

            elif msg_type == "ping":
                await ws_manager.send(ws, {"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)
