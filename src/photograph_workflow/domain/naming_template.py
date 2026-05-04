from __future__ import annotations

import re
from datetime import datetime

from photograph_workflow.config import DEFAULT_RENAME_TEMPLATE

from .sanitize import sanitize_filename_part

SUPPORTED_DATE_FORMATS = {
    "YYYYMMDD": "%Y%m%d",
    "YYYY-MM-DD": "%Y-%m-%d",
    "YYMMDD": "%y%m%d",
    "HHMMSS": "%H%M%S",
    "HH:mm:ss": "%H:%M:%S",
    "YYYYMMDDTHHMMSS": "%Y%m%dT%H%M%S",
    "YYYY-MM-DDTHH:mm:ss": "%Y-%m-%dT%H:%M:%S",
}

TOKEN_RE = re.compile(r"\{([^{}:]+)(?::([^{}]+))?\}")


class TemplateError(ValueError):
    pass


def title_from_directory_name(directory_name: str) -> str:
    match = re.match(r"^\d{8}[-_](.+)$", directory_name)
    if match:
        return match.group(1)
    return directory_name


def render_template(
    template: str | None,
    *,
    folder: str,
    parent: str,
    relative_dir: str,
    title: str,
    date: datetime,
    original: str,
) -> str:
    actual_template = template or DEFAULT_RENAME_TEMPLATE

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        fmt = match.group(2)
        if token == "date":
            date_format = fmt or "YYYYMMDD"
            if date_format not in SUPPORTED_DATE_FORMATS:
                raise TemplateError(f"unsupported date format: {date_format}")
            return date.strftime(SUPPORTED_DATE_FORMATS[date_format])
        if fmt:
            raise TemplateError(f"token does not support format: {token}")
        values = {
            "folder": folder,
            "title": title,
            "parent": parent,
            "relative_dir": relative_dir,
            "original": original,
        }
        if token not in values:
            raise TemplateError(f"unsupported token: {token}")
        return sanitize_filename_part(values[token])

    return TOKEN_RE.sub(replace, actual_template)
