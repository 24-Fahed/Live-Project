"""网关基础设施层的运行时配置。

这份配置主要回答一个常见问题：
当项目需要向前端、管理端或媒体接口返回“对外可访问地址”时，
网关究竟应该使用哪一个基础地址。

当前规则刻意保持简单：
1. 如果启用了域名模式，优先使用 ``PUBLIC_BASE_URL``。
2. 否则按当前运行模式选择地址。
3. 如果没有显式配置运行模式，则回退到 ``APP_ENV``。
4. 如果两者都没有，则按 ``local`` 处理。
"""

from pydantic_settings import BaseSettings


class RuntimeSettings(BaseSettings):
    """描述网关当前处于哪个部署阶段、应当返回哪类外部地址。

    ``APP_ENV`` 表示较宽泛的环境标签，例如 ``local``、``staging``、
    ``production``。

    ``APP_RUNTIME_MODE`` 表示网关当前真正采用的运行行为。它通常与
    ``APP_ENV`` 保持一致，但我们仍然保留这两个字段，原因是：

    - ``APP_ENV`` 是开发和部署场景里更常见的命名。
    - ``APP_RUNTIME_MODE`` 更明确地表达“网关应当采用哪种运行策略”。

    如果 ``APP_RUNTIME_MODE`` 为空，代码会自动回退到 ``APP_ENV``，
    这样较简单的环境配置文件也可以继续工作。
    """

    # 部署阶段标签，常见值为：local / staging / production。
    APP_ENV: str = "local"

    # 运行行为开关。若已配置，则优先级高于 APP_ENV。
    APP_RUNTIME_MODE: str = "local"

    # 为 True 时，对外返回的地址优先使用域名入口。
    USE_DOMAIN: bool = False

    # v0.1.2 中加入的同义开关，让环境文件语义更直观。
    DOMAIN_ENABLED: bool = False

    # 为 True 时，表示当前部署预期具备公网 IP 可访问能力。
    USE_PUBLIC_IP: bool = False

    # 本地开发和本地 Docker 调试使用的基础地址。
    LOCAL_BASE_URL: str = "http://127.0.0.1:8080"

    # staging 公网集成测试阶段使用的基础地址。
    STAGING_BASE_URL: str = "http://127.0.0.1:8080"

    # 生产环境或域名入口启用后对外使用的基础地址。
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8080"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def domain_enabled(self) -> bool:
        """返回当前是否启用了域名模式。"""

        return bool(self.DOMAIN_ENABLED or self.USE_DOMAIN)

    @property
    def current_base_url(self) -> str:
        """返回当前网关应当向外部暴露的基础地址。

        为什么这里优先判断 ``APP_RUNTIME_MODE``？
        因为网关在生成 Admin、小程序、媒体接口返回值时，需要一个
        “当前生效中的运行模式”来决定应该给出哪个入口地址。
        ``APP_RUNTIME_MODE`` 就承担这个职责。

        回退顺序如下：
        - ``APP_RUNTIME_MODE``
        - ``APP_ENV``
        - ``local``

        这里的 ``local`` 表示：当前没有启用 staging 或 production 的
        特殊行为，因此回退到本地开发地址。
        """

        mode = (self.APP_RUNTIME_MODE or self.APP_ENV or "local").lower()

        # 域名模式的优先级高于环境标签。一旦系统明确要求使用域名，
        # 所有对外返回的地址都应直接使用 PUBLIC_BASE_URL。
        if self.domain_enabled:
            return self.PUBLIC_BASE_URL.rstrip("/")

        # production 返回最终对外入口地址。
        if mode == "production":
            return self.PUBLIC_BASE_URL.rstrip("/")

        # staging 返回公网联调阶段的外部地址。
        if mode == "staging":
            return self.STAGING_BASE_URL.rstrip("/")

        # 其余情况统一回退到本地开发地址。
        return self.LOCAL_BASE_URL.rstrip("/")

    @property
    def current_ws_base_url(self) -> str:
        """根据 ``current_base_url`` 推导当前应使用的 WebSocket 地址。"""

        base_url = self.current_base_url
        if base_url.startswith("https://"):
            return "wss://" + base_url[len("https://"):]
        if base_url.startswith("http://"):
            return "ws://" + base_url[len("http://"):]
        return base_url


runtime_settings = RuntimeSettings()
