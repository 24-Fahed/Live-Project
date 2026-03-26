HLS_HOST = "0.0.0.0"
HLS_PORT = 8443
HLS_BASE_DIR = "static/hls"
HLS_MOUNT_PREFIX = "/hls"

# SSL 开关：Docker 环境下由 Cloudflare Tunnel 提供 HTTPS，设为 false
HLS_ENABLE_SSL = False

# 证书配置（相对路径，基于项目根目录）
CERT_DIR = "app/subsystems/hls/certs"
CERT_FILE = f"{CERT_DIR}/server.crt"
KEY_FILE = f"{CERT_DIR}/server.key"

# 证书生成配置
CERT_VALIDITY_DAYS = 3650  # 10年
CERT_COMMON_NAME = "localhost"
CERT_SAN_NAMES = ["localhost", "127.0.0.1", "0.0.0.0"]
