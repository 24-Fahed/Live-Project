from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger


class VoteService:
    def get_votes(self, stream_id: str = "default") -> dict:
        data = repository.get_votes(stream_id)
        total = data["leftVotes"] + data["rightVotes"]
        if total == 0:
            return {**data, "totalVotes": 0, "leftPercentage": 0, "rightPercentage": 0}
        return {
            **data,
            "totalVotes": total,
            "leftPercentage": round(data["leftVotes"] / total * 100, 1),
            "rightPercentage": round(data["rightVotes"] / total * 100, 1),
        }

    async def user_vote(self, stream_id: str, left: int, right: int) -> dict:
        active = ws_manager.get_stream_viewers(stream_id)
        repository.add_votes(stream_id, left, right, active_users=active)
        result = self.get_votes(stream_id)
        await ws_manager.broadcast({
            "type": "votes-updated",
            "data": {**result, "streamId": stream_id},
        })
        logger.info("Vote updated", extra={"module": "stream", "stream_id": stream_id})
        return result

    async def admin_update_votes(self, stream_id: str, left: int, right: int, action: str = "set") -> dict:
        active = ws_manager.get_stream_viewers(stream_id)
        if action == "add":
            repository.add_votes(stream_id, left, right, active_users=active)
        else:
            repository.set_votes(stream_id, left, right, active_users=active)
        result = self.get_votes(stream_id)
        await ws_manager.broadcast({
            "type": "votes-updated",
            "data": {**result, "streamId": stream_id},
        })
        return result

    async def admin_set_votes(self, stream_id: str, left: int, right: int) -> dict:
        active = ws_manager.get_stream_viewers(stream_id)
        repository.set_votes(stream_id, left, right, active_users=active)
        result = self.get_votes(stream_id)
        await ws_manager.broadcast({
            "type": "votes-updated",
            "data": {**result, "streamId": stream_id},
        })
        return result

    async def reset_votes(self, stream_id: str, reset_to: dict | None = None, save_backup: bool = True) -> dict:
        active = ws_manager.get_stream_viewers(stream_id)
        repository.reset_votes(stream_id, reset_to, save_backup, active_users=active)
        result = self.get_votes(stream_id)
        await ws_manager.broadcast({
            "type": "votes-updated",
            "data": {**result, "streamId": stream_id},
        })
        logger.info("Votes reset", extra={"module": "stream", "stream_id": stream_id, "save_backup": save_backup})
        return result


vote_service = VoteService()
