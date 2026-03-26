from datetime import datetime, timezone

from app.comm.ws.manager import ws_manager
from app.subsystems.stream.debate.service import debate_service
from app.subsystems.stream.live.service import live_service
from app.subsystems.stream.repository import repository
from app.subsystems.stream.vote.service import vote_service


class DashboardService:
    def get_dashboard(self, stream_id: str) -> dict:
        live_status = live_service.get_live_status(stream_id)
        debate = debate_service.get_debate(stream_id)
        votes = vote_service.get_votes(stream_id)
        ai_status = repository.get_ai_status(stream_id)

        # 计算直播时长（秒）
        live_duration = 0
        if live_status["isLive"] and live_status["startTime"]:
            start = datetime.fromisoformat(live_status["startTime"])
            live_duration = int((datetime.now(timezone.utc) - start).total_seconds())

        return {
            "isLive": live_status["isLive"],
            "liveStreamUrl": live_status["streamUrl"],
            "streamId": stream_id,
            "activeUsers": ws_manager.get_stream_viewers(stream_id) if live_status["isLive"] else 0,
            "debateTopic": debate,
            "liveStartTime": live_status["startTime"],
            "liveDuration": live_duration,
            "totalVotes": votes["totalVotes"],
            "leftVotes": votes["leftVotes"],
            "rightVotes": votes["rightVotes"],
            "leftPercentage": votes["leftPercentage"],
            "rightPercentage": votes["rightPercentage"],
            "aiStatus": ai_status["status"],
        }

    def get_viewers(self) -> dict:
        return {
            "totalConnections": ws_manager.get_total_connections(),
        }

    def get_viewers_count(self, stream_id: str) -> int:
        return ws_manager.get_stream_viewers(stream_id)


dashboard_service = DashboardService()
