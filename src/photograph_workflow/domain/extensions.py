from __future__ import annotations

from pathlib import Path

RAW_EXTENSIONS = {".arw", ".dng"}
SIDEcar_EXTENSIONS = {".xmp", ".acr", ".jpg", ".jpeg"}
SIDECAR_EXTENSIONS = SIDEcar_EXTENSIONS
POST_PROCESSOR_RISK_EXTENSIONS = {".lrcat", ".lrdata", ".cosessiondb", ".cocatalogdb"}


def normalized_suffix(path: Path) -> str:
    return path.suffix.lower()


def is_raw_candidate(path: Path) -> bool:
    return normalized_suffix(path) in RAW_EXTENSIONS


def is_sidecar_candidate(path: Path) -> bool:
    return normalized_suffix(path) in SIDECAR_EXTENSIONS


def is_supported_arw(path: Path) -> bool:
    return normalized_suffix(path) == ".arw"


def is_dng(path: Path) -> bool:
    return normalized_suffix(path) == ".dng"
