"""网关接入层配置。

这一层关注的是“系统如何对外暴露入口”，而不是具体业务逻辑。
它主要描述：
- 是否启用域名入口
- 是否启用 HTTPS / TLS
- 是否接入 Cloudflare
- 当前外部入口使用哪个端口与协议
"""

from pydantic_settings import BaseSettings


class EdgeSettings(BaseSettings):
    """描述网关在部署时如何对外暴露访问入口。"""

    # 当前运行中是否启用域名入口。
    DOMAIN_ENABLED: bool = False

    # 当前网关是否以 TLS 方式启动。
    HTTPS_ENABLED: bool = False

    # 当前部署是否预期接入 Cloudflare 的代理与 TLS 能力。
    CLOUDFLARE_ENABLED: bool = False

    # 兼容早期环境文件中只表达 DNS 能力的写法。
    USE_CLOUDFLARE_DNS: bool = False

    # 对外公开的域名，例如 example.com。
    PUBLIC_DOMAIN: str = ""

    # 文档与运行检查里使用的标准 HTTP / HTTPS 端口。
    HTTP_PORT: int = 80
    HTTPS_PORT: int = 443

    # 网关端口配置：兼容字段、容器内端口、宿主机暴露端口。
    GATEWAY_PORT: int = 8080
    GATEWAY_INTERNAL_PORT: int = 8080
    GATEWAY_BIND_PORT: int = 8080

    # 网关容器内的 TLS 证书与私钥路径。
    TLS_CERT_FILE: str = "/app/certs/origin.crt"
    TLS_KEY_FILE: str = "/app/certs/origin.key"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"

    @property
    def domain_enabled(self) -> bool:
        """返回接入层当前是否启用了域名模式。"""

        return bool(self.DOMAIN_ENABLED)

    @property
    def cloudflare_enabled(self) -> bool:
        """返回当前是否实际启用了 Cloudflare 相关能力。"""

        return bool(self.CLOUDFLARE_ENABLED or self.USE_CLOUDFLARE_DNS)

    @property
    def active_scheme(self) -> str:
        """返回当前接入层对外生效的协议。"""

        return "https" if self.HTTPS_ENABLED else "http"

    @property
    def active_port(self) -> int:
        """返回当前接入层对外生效的端口。"""

        return self.HTTPS_PORT if self.HTTPS_ENABLED else self.GATEWAY_BIND_PORT


edge_settings = EdgeSettings()
