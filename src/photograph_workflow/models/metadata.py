from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import Field

from photograph_workflow.config import METADATA_VERSION, WORKSPACE_VERSION

from .base import WorkflowModel
from .photo import DirectoryStatus, FileRole, FileStatus, WorkspaceKind


class MetadataFileEntry(WorkflowModel):
    original_name: str
    current_name: str
    planned_name: str | None = None
    role: FileRole
    status: FileStatus


class MetadataFile(WorkflowModel):
    version: int = METADATA_VERSION
    title: str | None = None
    template: str | None = None
    status: DirectoryStatus = DirectoryStatus.CONFIGURED
    created_at: datetime | None = None
    updated_at: datetime | None = None
    files: list[MetadataFileEntry] = Field(default_factory=list)


class WorkspaceEntry(WorkflowModel):
    id: str
    name: str
    path: Path
    kind: WorkspaceKind
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkspaceFile(WorkflowModel):
    version: int = WORKSPACE_VERSION
    workspaces: list[WorkspaceEntry] = Field(default_factory=list)
    default_workspace_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
