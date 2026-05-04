from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from photograph_workflow.adapters.workspace_xdg import XdgWorkspaceResolver
from photograph_workflow.application.archive import build_archive_plan, execute_archive
from photograph_workflow.application.archive_name import archive_name
from photograph_workflow.application.workspace import (
    add_workspace,
    list_workspaces,
    remove_workspace,
    set_default_workspace,
)
from photograph_workflow.models.photo import WorkspaceKind


def test_archive_plan_excludes_zip_but_keeps_metadata(tmp_path: Path) -> None:
    source = tmp_path / "Shanghai"
    source.mkdir()
    (source / ".metadata.json").write_text("{}", encoding="utf-8")
    (source / "photo.ARW").write_bytes(b"raw")
    (source / "old.zip").write_bytes(b"zip")
    output = tmp_path / "archive"

    plan = build_archive_plan(source, output)

    included = {item.source_path.name for item in plan.items if item.included}
    excluded = {item.source_path.name for item in plan.items if not item.included}
    assert ".metadata.json" in included
    assert "photo.ARW" in included
    assert "old.zip" in excluded


def test_execute_archive_writes_zip(tmp_path: Path) -> None:
    source = tmp_path / "Shanghai"
    source.mkdir()
    (source / "photo.ARW").write_bytes(b"raw")
    output = tmp_path / "archive"

    plan = execute_archive(source, output)

    assert not plan.errors
    assert plan.archive_path.exists()
    with ZipFile(plan.archive_path) as zip_file:
        assert f"{source.name}/photo.ARW" in zip_file.namelist()


def test_archive_name_warns_on_existing_target(tmp_path: Path) -> None:
    source = tmp_path / "Shanghai"
    output = tmp_path / "archive"
    source.mkdir()
    output.mkdir()
    plan = archive_name(source, output)
    if plan.archive_path:
        plan.archive_path.write_bytes(b"exists")
    second = archive_name(source, output, archived_at=plan.archived_at)
    assert second.warnings


def test_workspace_lifecycle(tmp_path: Path) -> None:
    store = tmp_path / "workspaces.json"
    resolver = XdgWorkspaceResolver(store)
    workspace_dir = tmp_path / "Photos"
    workspace_dir.mkdir()

    added = add_workspace(workspace_dir, name="Photos", kind=WorkspaceKind.LOCAL, resolver=resolver)
    assert not added.errors
    workspace_file = list_workspaces(resolver)
    workspace_id = workspace_file.workspaces[0].id

    assert not set_default_workspace(workspace_id, resolver=resolver).errors
    assert list_workspaces(resolver).default_workspace_id == workspace_id

    assert not remove_workspace(workspace_id, resolver=resolver).errors
    assert list_workspaces(resolver).workspaces == []
