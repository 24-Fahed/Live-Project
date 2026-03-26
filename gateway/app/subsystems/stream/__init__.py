from fastapi import APIRouter

from app.subsystems.stream.ai_content.router import router as ai_content_router
from app.subsystems.stream.dashboard.router import router as dashboard_router
from app.subsystems.stream.debate.router import router as debate_router
from app.subsystems.stream.statistics.router import router as statistics_router
from app.subsystems.stream.debate_flow.router import router as debate_flow_router
from app.subsystems.stream.judge.router import router as judge_router
from app.subsystems.stream.live.router import router as live_router
from app.subsystems.stream.user.router import router as user_router
from app.subsystems.stream.vote.router import router as vote_router

stream_router = APIRouter()
stream_router.include_router(live_router)
stream_router.include_router(vote_router)
stream_router.include_router(debate_router)
stream_router.include_router(debate_flow_router)
stream_router.include_router(ai_content_router)
stream_router.include_router(judge_router)
stream_router.include_router(user_router)
stream_router.include_router(dashboard_router)
stream_router.include_router(statistics_router)

__all__ = ["stream_router"]
