from app.infra.media_config.config import media_settings
from app.infra.runtime.config import runtime_settings
from app.utils.logger.logger import logger


class MediaService:
    def __init__(self):
        self._stream_statuses: dict[str, dict] = {}

    def build_push_url(self, stream_id: str) -> str:
        return f"{media_settings.current_push_base}/{stream_id}"

    def build_play_url(self, stream_id: str) -> str:
        base = runtime_settings.current_base_url
        prefix = media_settings.play_path_prefix
        return f"{base}{prefix}/{media_settings.SRS_APP}/{stream_id}.m3u8"

    def get_stream_info(self, stream_id: str) -> dict:
        status = self._stream_statuses.get(stream_id, {})
        return {
            "streamId": stream_id,
            "pushUrl": self.build_push_url(stream_id),
            "playUrl": self.build_play_url(stream_id),
            "publishStatus": status.get("publishStatus", "idle"),
            "lastEvent": status.get("lastEvent"),
            "lastPayload": status.get("lastPayload"),
        }

    def mark_event(self, event_name: str, payload: dict) -> dict:
        stream_id = payload.get("stream") or "unknown"
        publish_status = "live" if event_name == "on_publish" else "stopped"
        if event_name not in {"on_publish", "on_unpublish"}:
            publish_status = self._stream_statuses.get(stream_id, {}).get("publishStatus", "idle")

        self._stream_statuses[stream_id] = {
            "publishStatus": publish_status,
            "lastEvent": event_name,
            "lastPayload": payload,
        }
        logger.info("Media hook received", extra={"module": "media", "event": event_name, "stream_id": stream_id})
        return self.get_stream_info(stream_id)


media_service = MediaService()
