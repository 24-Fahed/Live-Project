import asyncio

from app.comm.ws.manager import ws_manager
from app.subsystems.ai.service import ai_service
from app.subsystems.stream.repository import repository
from app.utils.logger.logger import logger

VALID_ACTIONS = {"pause", "resume"}


class AIContentService:
    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._settings: dict[str, dict] = {}

    # ---- AI 内容 CRUD（原有） ----

    def list_contents(self, stream_id: str = "default") -> list[dict]:
        return repository.list_ai_contents(stream_id)

    def list_admin(self, page: int = 1, page_size: int = 20, stream_id: str | None = None) -> dict:
        return repository.list_ai_contents_admin(page, page_size, stream_id)

    def get_content(self, content_id: str) -> dict | None:
        return repository.get_ai_content(content_id)

    async def create_content(self, stream_id: str, content: str, side: str, confidence: float) -> dict:
        item = repository.create_ai_content(stream_id, content, side, confidence)
        await ws_manager.broadcast({
            "type": "newAIContent",
            "data": {
                "id": item["id"],
                "content": item["content"],
                "timestamp": item["timestamp"],
                "streamId": stream_id,
            },
        })
        logger.info("AI content created", extra={"module": "stream", "stream_id": stream_id})
        return item

    def delete_content(self, content_id: str) -> dict | None:
        return repository.delete_ai_content(content_id)

    def list_comments(self, content_id: str) -> list[dict]:
        return repository.list_ai_comments(content_id)

    def delete_comment(self, content_id: str, comment_id: str) -> dict | None:
        return repository.delete_ai_comment(content_id, comment_id)

    def add_comment(self, content_id: str, text: str, user: str, avatar: str) -> dict | None:
        """添加评论到 AI 内容。"""
        return repository.add_ai_comment(content_id, text, user, avatar)

    def add_like(self, content_id: str, comment_id: str | None = None) -> dict | None:
        """点赞 AI 内容或评论。"""
        return repository.add_ai_like(content_id, comment_id)

    # ---- AI 生命周期管理 ----

    async def start(self, stream_id: str, settings: dict) -> dict:
        # 如果已有运行中的任务，先停止
        if stream_id in self._tasks:
            await self._cancel_task(stream_id)

        self._settings[stream_id] = settings
        repository.set_ai_status(stream_id, "running", settings=settings)

        # 启动后台任务
        self._tasks[stream_id] = asyncio.create_task(self._content_loop(stream_id))

        await ws_manager.broadcast({
            "type": "aiStatus",
            "data": {"status": "running", "streamId": stream_id},
        })
        logger.info("AI started", extra={"module": "stream", "stream_id": stream_id})
        return repository.get_ai_status(stream_id)

    async def stop(self, stream_id: str) -> dict:
        await self._cancel_task(stream_id)
        self._settings.pop(stream_id, None)

        repository.set_ai_status(stream_id, "stopped")

        await ws_manager.broadcast({
            "type": "aiStatus",
            "data": {"status": "stopped", "streamId": stream_id},
        })
        logger.info("AI stopped", extra={"module": "stream", "stream_id": stream_id})
        return repository.get_ai_status(stream_id)

    async def toggle(self, stream_id: str, action: str) -> dict | None:
        if action not in VALID_ACTIONS:
            return None

        status_entry = repository.get_ai_status(stream_id)
        current_status = status_entry.get("status", "stopped")

        if action == "pause":
            if current_status != "running":
                return None
            await self._cancel_task(stream_id)
            repository.set_ai_status(stream_id, "paused", settings=self._settings.get(stream_id, {}))
        else:
            if current_status != "paused":
                return None
            self._tasks[stream_id] = asyncio.create_task(self._content_loop(stream_id))
            repository.set_ai_status(stream_id, "running", settings=self._settings.get(stream_id, {}))

        new_status = repository.get_ai_status(stream_id)
        await ws_manager.broadcast({
            "type": "aiStatus",
            "data": {"status": new_status["status"], "streamId": stream_id},
        })
        logger.info("AI toggled", extra={"module": "stream", "stream_id": stream_id, "action": action})
        return new_status

    async def get_status(self, stream_id: str) -> dict:
        return repository.get_ai_status(stream_id)

    # ---- 后台任务 ----

    async def _cancel_task(self, stream_id: str):
        task = self._tasks.pop(stream_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def _content_loop(self, stream_id: str):
        """后台任务：按间隔调用 ai_service.generate()，存储结果，广播"""
        try:
            while True:
                settings = self._settings.get(stream_id, {})
                interval = settings.get("interval", 5)

                await asyncio.sleep(interval)

                result = await ai_service.generate(
                    prompt="分析当前辩论内容",
                    context=f"stream: {stream_id}",
                    config=settings,
                )

                item = repository.create_ai_content(
                    stream_id, result.content, result.side, result.confidence,
                )
                await ws_manager.broadcast({
                    "type": "newAIContent",
                    "data": {
                        "id": item["id"],
                        "content": item["content"],
                        "timestamp": item["timestamp"],
                        "streamId": stream_id,
                        "side": result.side,
                        "confidence": result.confidence,
                    },
                })
                logger.info("AI content generated", extra={
                    "module": "stream", "stream_id": stream_id, "side": result.side,
                })
        except asyncio.CancelledError:
            logger.info("AI content loop cancelled", extra={"module": "stream", "stream_id": stream_id})
            raise


ai_content_service = AIContentService()
