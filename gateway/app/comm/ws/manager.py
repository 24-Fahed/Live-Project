import json

from fastapi import WebSocket

from app.utils.logger.logger import logger


class ConnectionManager:
    def __init__(self):
        self._clients: set[WebSocket] = set()
        self._client_info: dict[WebSocket, dict] = {}
        self._stream_viewers: dict[str, set[WebSocket]] = {}

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._clients.add(ws)
        logger.info("WS connected", extra={"module": "ws"})

    def disconnect(self, ws: WebSocket):
        self._clients.discard(ws)
        info = self._client_info.pop(ws, None)
        if info and "streamId" in info:
            self._remove_viewer(info["streamId"], ws)
        logger.info("WS disconnected", extra={"module": "ws"})

    def register(self, ws: WebSocket, info: dict):
        old_info = self._client_info.get(ws)
        old_stream_id = old_info.get("streamId") if old_info else None
        new_stream_id = info.get("streamId")

        if old_stream_id and old_stream_id != new_stream_id:
            self._remove_viewer(old_stream_id, ws)
        if new_stream_id:
            self._add_viewer(new_stream_id, ws)

        self._client_info[ws] = info
        logger.info("WS registered", extra={
            "module": "ws",
            "client_type": info.get("clientType"),
            "user_id": info.get("userId"),
            "stream_id": new_stream_id,
        })

    def _add_viewer(self, stream_id: str, ws: WebSocket):
        if stream_id not in self._stream_viewers:
            self._stream_viewers[stream_id] = set()
        self._stream_viewers[stream_id].add(ws)

    def _remove_viewer(self, stream_id: str, ws: WebSocket):
        viewers = self._stream_viewers.get(stream_id)
        if viewers:
            viewers.discard(ws)
            if not viewers:
                del self._stream_viewers[stream_id]

    async def broadcast(self, message: dict):
        data = json.dumps(message, ensure_ascii=False)
        dead = []
        for ws in self._clients:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send(self, ws: WebSocket, message: dict):
        try:
            await ws.send_json(message)
        except Exception:
            self.disconnect(ws)

    def get_total_connections(self) -> int:
        return len(self._clients)

    def get_stream_viewers(self, stream_id: str) -> int:
        viewers = self._stream_viewers.get(stream_id)
        return len(viewers) if viewers else 0

    def get_client_info(self, ws: WebSocket) -> dict | None:
        return self._client_info.get(ws)

    def get_online_user_ids(self) -> set[str]:
        """返回当前在线的用户 ID 集合"""
        ids = {
            info.get("userId")
            for info in self._client_info.values()
            if info.get("userId")
        }
        all_info = [info.get("userId") for info in self._client_info.values()]
        logger.info("get_online_user_ids called", extra={
            "module": "ws",
            "online_ids": list(ids),
            "all_user_ids_in_clients": all_info,
            "total_clients": len(self._clients),
        })
        return ids


ws_manager = ConnectionManager()
