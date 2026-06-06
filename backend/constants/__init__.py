# TODO: better place for this?
try:
    import os  # TODO: can this be removed?
    import shutil

    raw_window_width, raw_window_height = shutil.get_terminal_size()
except OSError:
    raw_window_width = 200

logging_prefix_offset = 40

window_width = max(
    abs(raw_window_width - logging_prefix_offset),
    120,
)

AIRROI_BASE_URL = "https://api.airroi.com"
