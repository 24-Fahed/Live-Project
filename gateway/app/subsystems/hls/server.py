import threading
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.subsystems.hls.config import HLS_HOST, HLS_PORT, HLS_BASE_DIR, HLS_MOUNT_PREFIX, HLS_ENABLE_SSL
from app.utils.logger.logger import logger


class HLSServer:
    """独立 HTTPS 静态文件服务器，用于托管 HLS 文件。"""

    def __init__(self):
        self._app: FastAPI | None = None
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None
        self._started = False

    @property
    def is_running(self) -> bool:
        """服务器是否运行中。"""
        return self._started and self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        """启动 HTTPS 服务器（阻塞）。"""
        if self._started:
            logger.warning("HLS server already started", extra={"module": "hls"})
            return

        # 确保静态文件目录存在
        hls_dir = Path(HLS_BASE_DIR)
        hls_dir.mkdir(parents=True, exist_ok=True)

        # 确保 SSL 证书存在（仅 HTTPS 模式）
        if HLS_ENABLE_SSL:
            from app.subsystems.hls.certs import ensure_certs
            cert_file, key_file = ensure_certs()

        # 创建 FastAPI 应用
        self._app = FastAPI(title="HLS Server", version="1.0")

        # 挂载静态文件
        self._app.mount(
            HLS_MOUNT_PREFIX,
            StaticFiles(directory=str(hls_dir), html=False),
            name="hls",
        )

        # 配置 uvicorn
        ssl_kwargs = {}
        if HLS_ENABLE_SSL:
            ssl_kwargs = {"ssl_certfile": cert_file, "ssl_keyfile": key_file}

        config = uvicorn.Config(
            self._app,
            host=HLS_HOST,
            port=HLS_PORT,
            log_level="warning",
            **ssl_kwargs,
        )
        self._server = uvicorn.Server(config)
        self._started = True

        logger.info(
            "HLS server starting",
            extra={
                "module": "hls",
                "host": HLS_HOST,
                "port": HLS_PORT,
                "mount": f"{HLS_MOUNT_PREFIX} -> {HLS_BASE_DIR}",
            },
        )

        # 运行服务器（阻塞）
        self._server.run()

    def start_background(self) -> None:
        """后台启动 HTTPS 服务器（非阻塞）。"""
        if self._started:
            logger.warning("HLS server already started", extra={"module": "hls"})
            return

        # 在守护线程中启动
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止 HTTPS 服务器。"""
        if not self._started:
            logger.warning("HLS server not running", extra={"module": "hls"})
            return

        if self._server:
            self._server.should_exit = True

        # 等待线程结束（最多5秒）
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        self._started = False
        logger.info("HLS server stopped", extra={"module": "hls"})
