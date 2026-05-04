from __future__ import annotations

from pathlib import Path

from photograph_workflow.adapters.filesystem_local import LocalFileSystem
from photograph_workflow.domain.metadata_record import (
    dump_metadata,
    metadata_path,
    read_metadata_file,
)
from photograph_workflow.errors import METADATA_DEVIATION
from photograph_workflow.models.photo import DirectoryStatus, FileStatus
from photograph_workflow.models.plan import PlanIssue, RollbackPlan, RollbackPlanItem
from photograph_workflow.ports.clock import ClockPort, SystemClock
from photograph_workflow.ports.filesystem import FileSystemPort


def build_rollback_plan(photo_dir: Path) -> RollbackPlan:
    metadata, issue = read_metadata_file(photo_dir)
    errors: list[PlanIssue] = []
    if issue:
        errors.append(issue)
    if not metadata or not metadata.files:
        errors.append(
            PlanIssue(
                code=METADATA_DEVIATION,
                message="No metadata file mapping is available",
                path=photo_dir,
            )
        )
        return RollbackPlan(
            root=photo_dir, dry_run=True, items=[], errors=errors, requires_confirmation=True
        )
    items: list[RollbackPlanItem] = []
    planned_current = {entry.current_name for entry in metadata.files}
    for entry in metadata.files:
        current = photo_dir / entry.current_name
        target = photo_dir / entry.original_name
        if not current.exists():
            errors.append(
                PlanIssue(code=METADATA_DEVIATION, message="Current file is missing", path=current)
            )
        if target.exists() and entry.original_name not in planned_current:
            errors.append(
                PlanIssue(
                    code=METADATA_DEVIATION, message="Rollback target already exists", path=target
                )
            )
        items.append(
            RollbackPlanItem(
                current_path=current,
                target_original_path=target,
                role=entry.role,
                status=FileStatus.PENDING,
            )
        )
    return RollbackPlan(
        root=photo_dir, dry_run=True, items=items, errors=errors, requires_confirmation=True
    )


def execute_rollback(
    photo_dir: Path, *, filesystem: FileSystemPort | None = None, clock: ClockPort | None = None
) -> RollbackPlan:
    plan = build_rollback_plan(photo_dir)
    plan.dry_run = False
    if plan.errors:
        return plan
    fs = filesystem or LocalFileSystem()
    for item in plan.items:
        if item.current_path != item.target_original_path:
            fs.rename(item.current_path, item.target_original_path)
    metadata, _issue = read_metadata_file(photo_dir)
    if metadata:
        now = (clock or SystemClock()).now()
        metadata.status = DirectoryStatus.ROLLED_BACK
        metadata.updated_at = now
        for entry in metadata.files:
            entry.current_name = entry.original_name
            entry.planned_name = None
            entry.status = FileStatus.ROLLED_BACK
        fs.write_json(metadata_path(photo_dir), dump_metadata(metadata))
    return plan
