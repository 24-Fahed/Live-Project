"""Static mount table for the FastAPI gateway.

Each tuple means:
``(mount_path, directory, html_mode)``.
"""

from pathlib import Path

# Static mount registration table:
# - /admin serves the built Admin front-end and therefore enables HTML mode.
# - /static serves shared static assets such as icons and scripts.
_MOUNTS: list[tuple[str, str, bool]] = [
    ("/admin", "static/admin", True),
    ("/static", "static", False),
]
