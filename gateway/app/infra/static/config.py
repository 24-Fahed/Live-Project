"""FastAPI 网关的静态资源挂载表。

这里集中维护静态目录的挂载规则，避免把路径信息分散写进主程序。
"""

from pathlib import Path


# 静态挂载注册表：
# - /admin 用于托管后台管理前端，因此需要开启 HTML 模式。
# - /static 用于托管共享静态资源，例如图标、脚本等。
STATIC_MOUNTS = [
    ("/admin", Path("static/admin"), True),
    ("/static", Path("static"), False),
]
