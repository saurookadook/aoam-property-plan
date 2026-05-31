from __future__ import annotations

import logging

from config.env_var_manager import EnvVarManager
from constants import window_width
from utils.logging.extended_logger import ExtendedLogger

root_logger = logging.getLogger()

env_vars = EnvVarManager().env_vars


def is_prod():
    return env_vars.env.lower() in set(["prod", "production"])


def init_logging(app_name: str):
    if is_prod():
        console_handler = logging.StreamHandler()
    else:
        from rich.logging import RichHandler

        console_handler = RichHandler(
            show_time=False, rich_tracebacks=True, tracebacks_theme="emacs"
        )

    root_logger.setLevel(getattr(logging, env_vars.log_level.upper()))

    format_str = (
        # "{asctime} [{name}: {lineno}] [{levelname:<10s}]: {message:<"
        "{asctime} [{name}: {lineno}]: {message:<"
        + str(window_width)
        + "s}"
    )
    console_handler.setFormatter(logging.Formatter(format_str, style="{"))
    root_logger.addHandler(console_handler)

    logging.setLoggerClass(ExtendedLogger)

    return root_logger
