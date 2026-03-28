from pathlib import Path

# (mount_path, local_directory, html_mode)
_MOUNTS: list[tuple[str, str, bool]] = [
    ('/admin', 'static/admin', True),
    ('/static', 'static', False),
]
