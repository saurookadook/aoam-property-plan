from __future__ import annotations

import logging
from enum import IntEnum


class LogLevel(IntEnum):

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def level_values(cls):
        return [level.value for level in cls]
