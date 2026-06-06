from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


def get_module_root(file: str) -> Path:
    """
    From the given ``file``, resolves to the root directory of the module: ``aoam-property-plan/backend``.
    """

    return scan_for_directory(
        file,
        lambda p: p.name == "backend" and p.parent.name == "aoam-property-plan",
        log_dir_name="module root",
    )


def get_project_root(file: str) -> Path:
    """
    From the given ``file``, resolves to the root directory of the project: ``aoam-property-plan``.
    """

    return scan_for_directory(
        file,
        lambda p: p.name == "aoam-property-plan",
        log_dir_name="project root",
    )


def scan_for_directory(
    file: str, is_target_dir_func: Callable[[Path], bool], log_dir_name: str = "target"
) -> Path:
    """Scans parent directories for a directory that matches the provided function."""
    file_path = Path(file)

    while (
        file_path.parent is not None
        # NOTE: probably a better way to handle filesystem root...
        and file_path.parent != file_path
        and file_path.parent.parent != file_path
    ):
        if file_path.is_dir() and is_target_dir_func(file_path):
            return file_path
        file_path = file_path.parent

    logger.warning(
        f"Could not find {log_dir_name} directory. Returning `Path` for provided file '{file}'."
    )
    return file_path
