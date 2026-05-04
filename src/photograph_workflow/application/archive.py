from __future__ import annotations

from datetime import datetime
from pathlib import Path

from photograph_workflow.adapters.archive_zipfile import ZipArchiveWriter
from photograph_workflow.domain.archive_rules import (
    count_raw_and_sidecar,
    exclude_reason,
)
from photograph_workflow.errors import ARCHIVE_TARGET_EXISTS
from photograph_workflow.models.plan import ArchivePlan, ArchivePlanItem, PlanIssue
from photograph_workflow.ports.archive_writer import ArchiveWriterPort
from photograph_workflow.ports.clock import ClockPort, SystemClock


def build_archive_plan(
    source_dir: Path,
    output_dir: Path,
    *,
    archived_at: datetime | None = None,
    overwrite: bool = False,
    clock: ClockPort | None = None,
) -> ArchivePlan:
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    timestamp = archived_at or (clock or SystemClock()).now()
    archive_path = output_dir / f"{source_dir.name}~{timestamp.strftime('%Y%m%d%H%M%S')}.zip"
    errors: list[PlanIssue] = []
    if archive_path.exists() and not overwrite:
        errors.append(
            PlanIssue(
                code=ARCHIVE_TARGET_EXISTS,
                message="Archive target already exists",
                path=archive_path,
            )
        )
    items: list[ArchivePlanItem] = []
    included_paths: list[Path] = []
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        reason = exclude_reason(path, source_dir)
        included = reason is None
        if included:
            included_paths.append(path)
        items.append(
            ArchivePlanItem(
                source_path=path,
                archive_path=archive_path,
                size_bytes=path.stat().st_size,
                included=included,
                exclude_reason=reason,
            )
        )
    raw_count, sidecar_count = count_raw_and_sidecar(included_paths)
    return ArchivePlan(
        root=source_dir,
        dry_run=True,
        source_dir=source_dir,
        archive_path=archive_path,
        archived_at=timestamp,
        overwrite=overwrite,
        total_size_bytes=sum(item.size_bytes or 0 for item in items if item.included),
        included_count=sum(1 for item in items if item.included),
        excluded_count=sum(1 for item in items if not item.included),
        raw_count=raw_count,
        sidecar_count=sidecar_count,
        items=items,
        errors=errors,
        requires_confirmation=True,
    )


def execute_archive(
    source_dir: Path,
    output_dir: Path,
    *,
    archived_at: datetime | None = None,
    overwrite: bool = False,
    archive_writer: ArchiveWriterPort | None = None,
    clock: ClockPort | None = None,
) -> ArchivePlan:
    plan = build_archive_plan(
        source_dir, output_dir, archived_at=archived_at, overwrite=overwrite, clock=clock
    )
    plan.dry_run = False
    if plan.errors:
        return plan
    writer = archive_writer or ZipArchiveWriter()
    writer.write_zip(plan.archive_path, source_dir, plan.items, overwrite=overwrite)
    return plan
