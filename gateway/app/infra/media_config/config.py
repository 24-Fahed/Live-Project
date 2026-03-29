"""媒体集成层配置。

这些配置属于媒体基础设施接入层，而不是业务层。
它们主要描述：
- 网关如何连接 SRS
- 不同环境下应返回哪个推流地址
- 当需要兜底重建 HLS 播放清单时应使用哪些本地参数
"""

from pydantic_settings import BaseSettings

from app.infra.runtime.config import runtime_settings


class MediaSettings(BaseSettings):
    """描述网关与 SRS 媒体服务之间的集成参数。"""

    # 当前部署中 SRS 的 Docker 服务名或主机名。
    SRS_HOST: str = "srs"

    # OBS 等推流端接入 SRS 使用的 RTMP 端口。
    SRS_RTMP_PORT: int = 1935

    # 网关从 SRS 读取 HLS 文件时使用的 HTTP 端口。
    SRS_HTTP_PORT: int = 8088

    # SRS 的应用名，因此当前播放地址会形如 /live/live/*.m3u8。
    SRS_APP: str = "live"

    # 网关对外暴露的 HLS 播放前缀。
    SRS_PLAY_PATH_PREFIX: str = "/live"

    # 是否允许 OBS 直接向公网 IP 推流。
    ALLOW_DIRECT_IP_PUSH: bool = True

    # 本地 Docker 调试时使用的推流基础地址。
    LOCAL_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    # staging 公网集成测试阶段使用的推流基础地址。
    STAGING_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    # 生产环境使用的推流基础地址。
    PRODUCTION_PUSH_BASE: str = "rtmp://127.0.0.1:1935/live"

    # SRS 回调到网关时使用的共享密钥。
    SRS_CALLBACK_TOKEN: str = "replace-me"

    # 受保护的媒体管理操作预留令牌。
    MEDIA_ADMIN_TOKEN: str = "replace-me"

    # 当网关需要根据磁盘中的现有文件重建 HLS 清单时，使用的兜底目录。
    SRS_FALLBACK_HLS_DIR: str = "/app/runtime/srs-html"

    # 兜底清单中保留的最近分片数量。
    SRS_FALLBACK_SEGMENT_WINDOW: int = 6

    # 兜底清单生成时使用的目标分片时长。
    SRS_FALLBACK_SEGMENT_DURATION: int = 5

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def http_upstream_base(self) -> str:
        """返回网关代理 SRS HTTP 资源时使用的上游基础地址。"""

        return f"http://{self.SRS_HOST}:{self.SRS_HTTP_PORT}"

    @property
    def play_path_prefix(self) -> str:
        """将播放前缀规范化为单个前导斜杠路径。"""

        return "/" + self.SRS_PLAY_PATH_PREFIX.strip("/")

    @property
    def current_push_base(self) -> str:
        """返回当前运行阶段应使用的 RTMP 推流基础地址。

        这里的运行阶段选择规则与 ``RuntimeSettings`` 保持一致，
        目的是避免用户需要学习两套不同的环境切换模型。
        """

        mode = (runtime_settings.APP_RUNTIME_MODE or runtime_settings.APP_ENV or "local").lower()
        if mode == "production":
            return self.PRODUCTION_PUSH_BASE.rstrip("/")
        if mode == "staging":
            return self.STAGING_PUSH_BASE.rstrip("/")
        return self.LOCAL_PUSH_BASE.rstrip("/")


media_settings = MediaSettings()
