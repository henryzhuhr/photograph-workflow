from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from photograph_workflow.adapters.workspace_xdg import XdgWorkspaceResolver
from photograph_workflow.errors import WORKSPACE_NOT_FOUND, WORKSPACE_PATH_INVALID
from photograph_workflow.models.metadata import WorkspaceEntry, WorkspaceFile
from photograph_workflow.models.photo import WorkspaceKind
from photograph_workflow.models.plan import CommonPlan, PlanIssue
from photograph_workflow.ports.workspace_resolver import WorkspaceResolverPort


def list_workspaces(resolver: WorkspaceResolverPort | None = None) -> WorkspaceFile:
    return (resolver or XdgWorkspaceResolver()).load()


def add_workspace(
    path: Path,
    *,
    name: str | None = None,
    kind: WorkspaceKind = WorkspaceKind.CUSTOM,
    resolver: WorkspaceResolverPort | None = None,
) -> CommonPlan:
    if not path.exists() or not path.is_dir():
        return CommonPlan(
            operation="workspace",
            root=path,
            dry_run=False,
            errors=[
                PlanIssue(
                    code=WORKSPACE_PATH_INVALID, message="Workspace path is invalid", path=path
                )
            ],
            requires_confirmation=False,
        )
    actual_resolver = resolver or XdgWorkspaceResolver()
    workspace_file = actual_resolver.load()
    now = datetime.now().astimezone()
    entry = WorkspaceEntry(
        id=str(uuid4()),
        name=name or path.name,
        path=path,
        kind=kind,
        created_at=now,
        updated_at=now,
    )
    workspace_file.workspaces.append(entry)
    workspace_file.updated_at = now
    if not workspace_file.default_workspace_id:
        workspace_file.default_workspace_id = entry.id
    actual_resolver.save(workspace_file)
    return CommonPlan(
        operation="workspace", root=path, dry_run=False, items=[entry], requires_confirmation=False
    )


def set_default_workspace(
    workspace_id: str, *, resolver: WorkspaceResolverPort | None = None
) -> CommonPlan:
    actual_resolver = resolver or XdgWorkspaceResolver()
    workspace_file = actual_resolver.load()
    if workspace_id not in {entry.id for entry in workspace_file.workspaces}:
        return CommonPlan(
            operation="workspace",
            root=Path("."),
            dry_run=False,
            errors=[PlanIssue(code=WORKSPACE_NOT_FOUND, message="Workspace not found")],
            requires_confirmation=False,
        )
    workspace_file.default_workspace_id = workspace_id
    workspace_file.updated_at = datetime.now().astimezone()
    actual_resolver.save(workspace_file)
    return CommonPlan(
        operation="workspace",
        root=Path("."),
        dry_run=False,
        items=[workspace_file],
        requires_confirmation=False,
    )


def remove_workspace(
    workspace_id: str, *, resolver: WorkspaceResolverPort | None = None
) -> CommonPlan:
    actual_resolver = resolver or XdgWorkspaceResolver()
    workspace_file = actual_resolver.load()
    kept = [entry for entry in workspace_file.workspaces if entry.id != workspace_id]
    if len(kept) == len(workspace_file.workspaces):
        return CommonPlan(
            operation="workspace",
            root=Path("."),
            dry_run=False,
            errors=[PlanIssue(code=WORKSPACE_NOT_FOUND, message="Workspace not found")],
            requires_confirmation=False,
        )
    workspace_file.workspaces = kept
    if workspace_file.default_workspace_id == workspace_id:
        workspace_file.default_workspace_id = kept[0].id if kept else None
    workspace_file.updated_at = datetime.now().astimezone()
    actual_resolver.save(workspace_file)
    return CommonPlan(
        operation="workspace",
        root=Path("."),
        dry_run=False,
        items=[workspace_file],
        requires_confirmation=False,
    )
