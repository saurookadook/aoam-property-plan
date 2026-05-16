from __future__ import annotations

import logging

from backend.config import env_vars
from backend.constants import window_width
from backend.logging.extended_logger import ExtendedLogger

logging.setLoggerClass(ExtendedLogger)

root_logger = logging.getLogger()


def is_prod():
    return env_vars.ENV.lower() == "prod"


def init_logging(app_name: str):
    if is_prod():
        console_handler = logging.StreamHandler()
    else:
        from rich.logging import RichHandler

        console_handler = RichHandler(
            show_time=False, rich_tracebacks=True, tracebacks_theme="emacs"
        )

    root_logger.setLevel(getattr(logging, env_vars.LOG_LEVEL.upper()))

    format_str = (
        # "{asctime} [{name}: {lineno}] [{levelname:<10s}]: {message:<"
        "{asctime} [{name}: {lineno}]: {message:<"
        + str(window_width)
        + "s}"
    )
    console_handler.setFormatter(logging.Formatter(format_str, style="{"))
    root_logger.addHandler(console_handler)
