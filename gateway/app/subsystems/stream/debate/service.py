from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger


class DebateService:
    def get_debate(self, stream_id: str) -> dict | None:
        return repository.get_debate(stream_id)

    def get_debate_by_id(self, debate_id: str) -> dict | None:
        return repository.get_debate_by_id(debate_id)

    async def create_debate(self, title: str, description: str, left: str, right: str, is_active: bool) -> dict:
        debate = repository.create_debate(title, description, left, right, is_active)
        logger.info("Debate created", extra={"module": "stream", "debate_id": debate["id"]})
        return debate

    async def update_debate(self, debate_id: str, **kwargs) -> dict | None:
        debate = repository.update_debate(debate_id, **kwargs)
        if debate:
            await ws_manager.broadcast({
                "type": "debate-updated",
                "data": debate,
            })
            logger.info("Debate updated", extra={"module": "stream", "debate_id": debate_id})
        return debate

    async def associate_debate(self, stream_id: str, debate_id: str) -> bool:
        ok = repository.associate_debate(stream_id, debate_id)
        if ok:
            debate = repository.get_debate(stream_id)
            if debate:
                await ws_manager.broadcast({
                    "type": "debate-updated",
                    "data": {**debate, "streamId": stream_id},
                })
            logger.info("Debate associated", extra={"module": "stream", "stream_id": stream_id, "debate_id": debate_id})
        return ok

    async def remove_stream_debate(self, stream_id: str) -> bool:
        ok = repository.remove_debate(stream_id)
        if ok:
            await ws_manager.broadcast({
                "type": "debate-updated",
                "data": {"streamId": stream_id, "debateTopic": None},
            })
            logger.info("Stream debate removed", extra={"module": "stream", "stream_id": stream_id})
        return ok


debate_service = DebateService()
