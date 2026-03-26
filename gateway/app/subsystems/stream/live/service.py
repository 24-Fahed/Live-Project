from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger


class LiveService:
    # ---- 流管理 ----

    def list_streams(self) -> dict:
        streams = repository.list_streams()
        return {"streams": streams, "total": len(streams)}

    def get_stream(self, stream_id: str) -> dict | None:
        return repository.get_stream(stream_id)

    def create_stream(self, name: str, url: str | None, type_: str, description: str) -> dict:
        stream = repository.create_stream(name, url or "", type_, description)
        return stream

    def update_stream(self, stream_id: str, **kwargs) -> dict | None:
        return repository.update_stream(stream_id, **kwargs)

    def delete_stream(self, stream_id: str) -> dict | None:
        stream = repository.get_stream(stream_id)
        if not stream:
            return None
        return repository.delete_stream(stream_id)

    # ---- 直播控制 ----

    def get_live_status(self, stream_id: str = "default") -> dict:
        return repository.get_live_status(stream_id)

    async def start_live(self, stream_id: str) -> dict:
        status = repository.start_live(stream_id)
        await ws_manager.broadcast({
            "type": "liveStatus",
            "data": status,
        })
        logger.info("Live started", extra={"module": "stream", "stream_id": stream_id})
        return status

    async def stop_live(self, stream_id: str) -> dict:
        result = repository.stop_live(stream_id)
        await ws_manager.broadcast({
            "type": "liveStatus",
            "data": {"isLive": False, "streamId": stream_id},
        })
        logger.info("Live stopped", extra={"module": "stream", "stream_id": stream_id})
        return result

    def get_viewers_count(self, stream_id: str) -> int:
        return ws_manager.get_stream_viewers(stream_id)


live_service = LiveService()
