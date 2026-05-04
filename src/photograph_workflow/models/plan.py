from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from .base import WorkflowModel
from .photo import FileRole, FileStatus


class PlanIssue(WorkflowModel):
    code: str
    message: str
    path: Path | None = None
    details: dict[str, Any] | None = None


class CommonPlan(WorkflowModel):
    operation: str
    root: Path
    dry_run: bool = True
    items: list[Any] = Field(default_factory=list)
    warnings: list[PlanIssue] = Field(default_factory=list)
    errors: list[PlanIssue] = Field(default_factory=list)
    metadata_changes: list[Any] = Field(default_factory=list)
    requires_confirmation: bool = True


class RenamePlanItem(WorkflowModel):
    source_path: Path
    target_path: Path
    role: FileRole
    raw_source_path: Path | None = None
    original_name: str
    current_name: str
    planned_name: str | None = None
    status: FileStatus


class RenamePlan(CommonPlan):
    operation: Literal["rename"] = "rename"
    items: list[RenamePlanItem] = Field(default_factory=list)


class RollbackPlanItem(WorkflowModel):
    current_path: Path
    target_original_path: Path
    role: FileRole
    status: FileStatus


class RollbackPlan(CommonPlan):
    operation: Literal["rollback"] = "rollback"
    items: list[RollbackPlanItem] = Field(default_factory=list)


class ArchivePlanItem(WorkflowModel):
    source_path: Path
    archive_path: Path
    size_bytes: int | None = None
    included: bool
    exclude_reason: str | None = None


class ArchivePlan(CommonPlan):
    operation: Literal["archive"] = "archive"
    source_dir: Path
    archive_path: Path
    archived_at: datetime
    overwrite: bool = False
    total_size_bytes: int = 0
    included_count: int = 0
    excluded_count: int = 0
    raw_count: int = 0
    sidecar_count: int = 0
    items: list[ArchivePlanItem] = Field(default_factory=list)


class ArchiveNamePlan(CommonPlan):
    operation: Literal["archive_name"] = "archive_name"
    source_dir: Path
    archive_name: str
    archive_path: Path | None = None
    archived_at: datetime
