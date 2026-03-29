"""Legacy HLS demo configuration.

This subsystem comes from an earlier demonstration stage of the project. It is no
longer the main media solution in the current architecture, where SRS handles
RTMP ingest and HLS output.

The configuration is kept only for historical compatibility and code reading.
"""

# Legacy demo host/port for the standalone HLS service.
HLS_HOST = "0.0.0.0"
HLS_PORT = 8443

# Local directory and public mount prefix used by the demo HLS service.
HLS_BASE_DIR = "static/hls"
HLS_MOUNT_PREFIX = "/hls"

# HTTPS switch for the legacy HLS demo service.
# In the current architecture, formal HTTPS is handled by the gateway
# infrastructure layer rather than by this demo module.
HLS_ENABLE_SSL = False

# Certificate locations used only when the legacy HLS demo enables SSL.
CERT_DIR = "app/subsystems/hls/certs"
CERT_FILE = f"{CERT_DIR}/server.crt"
KEY_FILE = f"{CERT_DIR}/server.key"

# Certificate generation defaults for the demo HLS service.
CERT_VALIDITY_DAYS = 3650  # 10 years
CERT_COMMON_NAME = "localhost"
CERT_SAN_NAMES = ["localhost", "127.0.0.1", "0.0.0.0"]
