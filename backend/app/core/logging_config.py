"""
Centralized logging configuration.

Call `configure_logging()` once, at application startup, so that every
module can simply do `logging.getLogger(__name__)` and get consistent,
readable log output.
"""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Configures root logging handlers, format, and level."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
