from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from photograph_workflow.config import METADATA_FILENAME, METADATA_VERSION
from photograph_workflow.errors import METADATA_VERSION_UNSUPPORTED
from photograph_workflow.models.metadata import MetadataFile
from photograph_workflow.models.plan import PlanIssue


def metadata_path(directory: Path) -> Path:
    return directory / METADATA_FILENAME


def read_metadata_file(directory: Path) -> tuple[MetadataFile | None, PlanIssue | None]:
    path = metadata_path(directory)
    if not path.exists():
        return None, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        version = payload.get("version")
        if not isinstance(version, int) or version != METADATA_VERSION:
            return None, PlanIssue(
                code=METADATA_VERSION_UNSUPPORTED,
                message=".metadata.json version is unsupported",
                path=path,
                details={"version": version},
            )
        return MetadataFile.model_validate(payload), None
    except (json.JSONDecodeError, ValidationError) as exc:
        return None, PlanIssue(
            code=METADATA_VERSION_UNSUPPORTED,
            message=".metadata.json is invalid",
            path=path,
            details={"error": str(exc)},
        )


def dump_metadata(metadata: MetadataFile) -> str:
    return metadata.model_dump_json(indent=2) + "\n"


def now_metadata_file(title: str | None, template: str | None, now: datetime) -> MetadataFile:
    return MetadataFile(title=title, template=template, created_at=now, updated_at=now)
