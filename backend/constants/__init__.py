# TODO: better place for this?
try:
    import os  # TODO: can this be removed?
    import shutil

    raw_window_width, _ = shutil.get_terminal_size()
except OSError:
    raw_window_width = 200

window_width = (
    raw_window_width - 160
)  # to account for characters added by logging handlers
