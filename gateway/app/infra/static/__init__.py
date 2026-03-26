from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.infra.static.config import _MOUNTS


def setup(app: FastAPI):
    for path, directory, html in _MOUNTS:
        dir_path = Path(directory)
        if dir_path.is_dir():
            app.mount(path, StaticFiles(directory=str(dir_path), html=html), name=f"static_{path}")
