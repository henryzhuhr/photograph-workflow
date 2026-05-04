from __future__ import annotations

from datetime import datetime
from pathlib import Path

from photograph_workflow.errors import ARCHIVE_NAME_TARGET_EXISTS
from photograph_workflow.models.plan import ArchiveNamePlan, PlanIssue
from photograph_workflow.ports.clock import ClockPort, SystemClock


def archive_name(
    source_dir: Path,
    output_dir: Path | None = None,
    archived_at: datetime | None = None,
    clock: ClockPort | None = None,
) -> ArchiveNamePlan:
    source_dir = source_dir.resolve()
    timestamp = archived_at or (clock or SystemClock()).now()
    name = f"{source_dir.name}~{timestamp.strftime('%Y%m%d%H%M%S')}.zip"
    archive_path = output_dir / name if output_dir else None
    warnings = []
    if archive_path and archive_path.exists():
        warnings.append(
            PlanIssue(
                code=ARCHIVE_NAME_TARGET_EXISTS,
                message="Recommended archive path already exists",
                path=archive_path,
            )
        )
    return ArchiveNamePlan(
        root=source_dir,
        dry_run=True,
        source_dir=source_dir,
        archive_name=name,
        archive_path=archive_path,
        archived_at=timestamp,
        warnings=warnings,
        requires_confirmation=False,
    )
