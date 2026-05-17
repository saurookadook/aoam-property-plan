from __future__ import annotations

import logging
from typing import Any

from rich import pretty

from backend.constants import raw_window_width, window_width
from backend.logging.log_level import LogLevel

BaseLoggerClass = logging.getLoggerClass()


class ExtendedLogger(BaseLoggerClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raw_window_width = raw_window_width
        self.window_width = max(100, window_width)

    # TODO: type annotation for "int in this Enum"?
    def log_centered(
        self, log_level: int, msg: str, *args, fill_char: str = "-", **kwargs
    ):
        self._log_impl(
            log_level, msg.center(self.window_width, fill_char), *args, **kwargs
        )

    def log_section_start(self, log_level: int, entity_name: str, *args, **kwargs):
        self._log_impl(
            log_level,
            f" 'Getting `{entity_name}` records...' ".center(self.window_width, "="),
            *args,
            **kwargs,
        )

    def log_section_end(
        self, log_level: int, entity_name: str, entity_count: int, *args, **kwargs
    ):
        self._log_impl(
            log_level,
            f" 'Done with `{entity_name}` records! Total: {entity_count}' ".center(
                self.window_width, "="
            ),
            *args,
            **kwargs,
        )

    def log_pretty(
        self,
        log_level: int,
        msg_obj: Any,
        *,
        max_width: int = window_width,
        indent_size: int = 4,
        max_length: int | None = None,
        max_string: int | None = None,
        max_depth: int | None = None,
        expand_all: bool = True,
        **kwargs,
    ):
        prettified_msg_obj = "\n" + pretty.pretty_repr(
            msg_obj,
            max_width=max_width,
            indent_size=indent_size,
            max_length=max_length,
            max_string=max_string,
            max_depth=max_depth,
            expand_all=expand_all,
        )

        self._log_impl(
            log_level,
            prettified_msg_obj,
            **kwargs,
        )

    def log_info_centered(self, *args, **kwargs):
        self.log_centered(LogLevel.INFO.value, *args, **kwargs)

    def log_info_section_start(self, *args, **kwargs):
        self.log_section_start(LogLevel.INFO.value, *args, **kwargs)

    def log_info_section_end(self, *args, **kwargs):
        self.log_section_end(LogLevel.INFO.value, *args, **kwargs)

    def log_info_pretty(self, msg_obj: Any, **kwargs):
        self.log_pretty(LogLevel.INFO.value, msg_obj, **kwargs)

    def log_debug_centered(self, *args, **kwargs):
        self.log_centered(LogLevel.DEBUG.value, *args, **kwargs)

    def log_debug_section_start(self, *args, **kwargs):
        self.log_section_start(LogLevel.DEBUG.value, *args, **kwargs)

    def log_debug_section_end(self, *args, **kwargs):
        self.log_section_end(LogLevel.DEBUG.value, *args, **kwargs)

    def log_debug_pretty(self, msg_obj: Any, **kwargs):
        self.log_pretty(LogLevel.DEBUG.value, msg_obj, **kwargs)

    def log_warn_centered(self, *args, **kwargs):
        self.log_centered(LogLevel.WARNING.value, *args, **kwargs)

    def log_warn_section_start(self, *args, **kwargs):
        self.log_section_start(LogLevel.WARNING.value, *args, **kwargs)

    def log_warn_section_end(self, *args, **kwargs):
        self.log_section_end(LogLevel.WARNING.value, *args, **kwargs)

    def log_warn_pretty(self, msg_obj: Any, **kwargs):
        self.log_pretty(LogLevel.WARNING.value, msg_obj, **kwargs)

    def log_error_centered(self, *args, **kwargs):
        self.log_centered(LogLevel.ERROR.value, *args, **kwargs)

    def log_error_section_start(self, *args, **kwargs):
        self.log_section_start(LogLevel.ERROR.value, *args, **kwargs)

    def log_error_section_end(self, *args, **kwargs):
        self.log_section_end(LogLevel.ERROR.value, *args, **kwargs)

    def log_error_pretty(self, msg_obj: Any, **kwargs):
        self.log_pretty(LogLevel.ERROR.value, msg_obj, **kwargs)

    def _log_impl(self, log_level: int, *args, **kwargs):
        if not isinstance(log_level, int) or log_level not in LogLevel.level_values():
            log_level = LogLevel.INFO.value
        self.log(log_level, *args, **kwargs)
