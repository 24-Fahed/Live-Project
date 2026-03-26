from datetime import datetime, timedelta, timezone

from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository


class StatisticsService:
    def get_votes_timeline(self, stream_id: str, time_range: str = "1h") -> dict:
        """返回投票趋势时间线数据，基于真实变更记录。

        time_range: "1h" | "6h" | "12h" | "24h" | "7d"
        """
        now = datetime.now(timezone.utc)
        delta_map = {"1h": 1, "6h": 6, "12h": 12, "24h": 24, "7d": 168}
        hours = delta_map.get(time_range, 1)
        since = now - timedelta(hours=hours)

        # 从 repository 获取真实快照
        snapshots = repository.get_vote_snapshots(stream_id, since)

        # 如果没有快照，返回空时间线
        if not snapshots:
            return {"timeline": [], "summary": self._build_summary(stream_id)}

        timeline = [
            {
                "time": s["time"],
                "leftVotes": s["leftVotes"],
                "rightVotes": s["rightVotes"],
                "total": s["total"],
                "activeUsers": s["activeUsers"],
            }
            for s in snapshots
        ]

        return {"timeline": timeline, "summary": self._build_summary(stream_id, timeline)}

    def _build_summary(self, stream_id: str, timeline: list[dict] | None = None) -> dict:
        votes = repository.get_votes(stream_id)
        left = votes["leftVotes"]
        right = votes["rightVotes"]
        peak = 0
        if timeline:
            peak = max((p["activeUsers"] for p in timeline), default=0)
        return {
            "totalVotes": left + right,
            "leftVotes": left,
            "rightVotes": right,
            "peakActiveUsers": peak,
        }


statistics_service = StatisticsService()
