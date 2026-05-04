from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

CAPTURE_TIME_FIELDS = (
    "SubSecDateTimeOriginal",
    "DateTimeOriginal",
    "SubSecCreateDate",
    "CreateDate",
    "ModifyDate",
)


def metadata_value(metadata: dict[str, Any], key: str) -> str | None:
    value = metadata.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def is_dji_dng(metadata: dict[str, Any]) -> bool:
    file_type = (metadata_value(metadata, "FileType") or "").upper()
    make = (metadata_value(metadata, "Make") or "").lower()
    model = (metadata_value(metadata, "Model") or "").lower()
    return file_type == "DNG" and ("dji" in make or "dji" in model)


def parse_exif_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    if "." in text:
        head, tail = text.split(".", 1)
        digits = "".join(ch for ch in tail if ch.isdigit())
        if digits:
            text = f"{head}.{digits[:6]}"
    for fmt in ("%Y:%m:%d %H:%M:%S.%f", "%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text[: len(datetime.now().strftime(fmt))], fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def capture_time(metadata: dict[str, Any]) -> datetime | None:
    for field in CAPTURE_TIME_FIELDS:
        value = metadata_value(metadata, field)
        if value:
            parsed = parse_exif_datetime(value)
            if parsed:
                return parsed
    return None


def metadata_source_path(metadata: dict[str, Any]) -> Path | None:
    source = metadata_value(metadata, "SourceFile")
    if source:
        return Path(source)
    directory = metadata_value(metadata, "Directory")
    filename = metadata_value(metadata, "FileName")
    if directory and filename:
        return Path(directory) / filename
    return None
