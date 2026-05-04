from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from .extensions import is_raw_candidate, is_sidecar_candidate

DEFAULT_EXCLUDES = (
    ".DS_Store",
    "._*",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    "Thumbs.db",
    "desktop.ini",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.part",
    "*.zip",
    "*.7z",
    "*.rar",
    "*.lrdata",
)


def exclude_reason(
    path: Path, root: Path, patterns: tuple[str, ...] = DEFAULT_EXCLUDES
) -> str | None:
    relative = path.relative_to(root)
    if path.name == ".metadata.json":
        return None
    for pattern in patterns:
        if fnmatch(path.name, pattern) or fnmatch(str(relative), pattern):
            return pattern
    return None


def count_raw_and_sidecar(paths: list[Path]) -> tuple[int, int]:
    return (
        sum(1 for path in paths if is_raw_candidate(path)),
        sum(1 for path in paths if is_sidecar_candidate(path)),
    )
