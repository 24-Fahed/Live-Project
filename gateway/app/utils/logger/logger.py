import sys

from loguru import logger

logger.remove()

logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<7} | {module}:{function}:{line} | {message}",
    level="DEBUG",
)
