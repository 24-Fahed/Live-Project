from pathlib import Path

# 静态资源挂载注册表
# (挂载路径, 目录, html模式)
_MOUNTS: list[tuple[str, str, bool]] = [
    ("/admin", "static/admin", True),
    ("/static", "static", False),
]
