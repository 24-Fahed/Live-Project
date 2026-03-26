from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger


class JudgeService:
    def get_judges(self, stream_id: str) -> list[dict]:
        return repository.get_judges(stream_id)

    async def save_judges(self, stream_id: str, judges: list[dict]) -> list[dict]:
        repository.set_judges(stream_id, judges)
        await ws_manager.broadcast({
            "type": "judges-updated",
            "data": {"streamId": stream_id, "judges": judges},
        })
        logger.info("Judges saved", extra={"module": "stream", "stream_id": stream_id, "count": len(judges)})
        return judges


judge_service = JudgeService()
