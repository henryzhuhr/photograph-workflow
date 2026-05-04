from __future__ import annotations

INVALID_CHARS = set('/\\:*?"<>|')


def is_valid_filename(name: str) -> bool:
    if not name or name in {".", ".."}:
        return False
    return not any(ch in INVALID_CHARS for ch in name)


def sanitize_filename_part(value: str) -> str:
    stripped = value.strip()
    return "".join("_" if ch in INVALID_CHARS else ch for ch in stripped)
