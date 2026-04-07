from loguru import logger
import sys
import os

import config.logs

# Ensure log directory exists before loguru tries to open any file sink.
# This runs at import time, before ensure_dirs() is ever called by the app.
os.makedirs("log", exist_ok=True)

logger.remove()

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan> | "
    "<cyan>{file}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level> | {extra!r}"
)

# stdout sink only when a real terminal exists.
# In a PyInstaller --console=False bundle sys.stdout is None;
# writing to it makes loguru retry indefinitely → infinite loop.
if not getattr(sys, 'frozen', False):
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="DEBUG",
        colorize=True,
    )

logger.add(
    config.logs.LOGS['debug'],
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
)
logger.add(
    config.logs.LOGS['error'],
    format=LOG_FORMAT,
    level="ERROR",
    rotation="500 MB",
    compression="zip",
)
logger.add(
    config.logs.LOGS['activity'],
    level="INFO",
    format=LOG_FORMAT,
    filter=lambda record: record["extra"].get("activity", False),
    enqueue=True,
)
