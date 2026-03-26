from app.comm.ws.manager import ws_manager
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger

VALID_ACTIONS = {"start", "pause", "resume", "reset", "next", "prev"}


class DebateFlowService:
    def get_flow(self, stream_id: str) -> dict:
        return repository.get_debate_flow(stream_id)

    async def save_flow(self, stream_id: str, segments: list[dict]) -> list[dict]:
        repository.set_debate_flow(stream_id, segments)
        await ws_manager.broadcast({
            "type": "debate-flow-updated",
            "data": {"streamId": stream_id, "flow": segments},
        })
        logger.info("Debate flow saved", extra={"module": "stream", "stream_id": stream_id, "segments": len(segments)})
        return segments

    async def control_flow(self, stream_id: str, action: str) -> dict:
        if action not in VALID_ACTIONS:
            raise ValueError(f"无效的操作: {action}")

        flow = repository.get_debate_flow(stream_id)
        segments = flow.get("segments", [])
        state = repository.get_debate_flow_state(stream_id)

        if action == "start":
            state["status"] = "running"
            state["currentSegmentIndex"] = 0
            state["remainingSeconds"] = segments[0]["duration"] if segments else 0

        elif action == "pause":
            state["status"] = "paused"

        elif action == "resume":
            state["status"] = "running"

        elif action == "reset":
            state["status"] = "idle"
            state["currentSegmentIndex"] = 0
            state["remainingSeconds"] = segments[0]["duration"] if segments else 0

        elif action == "next":
            idx = state.get("currentSegmentIndex", 0) + 1
            if idx < len(segments):
                state["currentSegmentIndex"] = idx
                state["remainingSeconds"] = segments[idx]["duration"]
            else:
                state["status"] = "idle"

        elif action == "prev":
            idx = state.get("currentSegmentIndex", 0) - 1
            if idx >= 0:
                state["currentSegmentIndex"] = idx
                state["remainingSeconds"] = segments[idx]["duration"]
            else:
                state["currentSegmentIndex"] = 0

        repository.update_debate_flow_state(stream_id, **state)

        await ws_manager.broadcast({
            "type": "debate-flow-control",
            "data": {"streamId": stream_id, "action": action, "state": state},
        })
        logger.info("Debate flow control", extra={"module": "stream", "stream_id": stream_id, "action": action})
        return state


debate_flow_service = DebateFlowService()
