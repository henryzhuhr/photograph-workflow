from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from photograph_workflow.application.archive import build_archive_plan, execute_archive
from photograph_workflow.application.archive_name import archive_name
from photograph_workflow.application.rename import build_rename_plan, execute_rename
from photograph_workflow.application.rollback import build_rollback_plan, execute_rollback
from photograph_workflow.application.scan import scan
from photograph_workflow.application.workspace import (
    add_workspace,
    list_workspaces,
    remove_workspace,
    set_default_workspace,
)
from photograph_workflow.models.input import BatchInput, DirectoryInput

WEB_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = WEB_DIR / "frontend" / "dist"
FRONTEND_INDEX = WEB_DIR / "frontend" / "index.html"

app = FastAPI(title="Photograph Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_json(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    return obj


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


@app.get("/api/workspaces")
def api_list_workspaces() -> Any:
    return _to_json(list_workspaces())


class AddWorkspaceBody(BaseModel):
    path: str
    name: str | None = None
    kind: str = "custom"


@app.post("/api/workspaces")
def api_add_workspace(body: AddWorkspaceBody) -> Any:
    from photograph_workflow.models.photo import WorkspaceKind

    valid_kinds = {e.value for e in WorkspaceKind}
    kind = WorkspaceKind(body.kind) if body.kind in valid_kinds else WorkspaceKind.CUSTOM
    return _to_json(add_workspace(Path(body.path), name=body.name, kind=kind))


@app.delete("/api/workspaces/{workspace_id}")
def api_remove_workspace(workspace_id: str) -> Any:
    return _to_json(remove_workspace(workspace_id))


@app.put("/api/workspaces/{workspace_id}/default")
def api_set_default_workspace(workspace_id: str) -> Any:
    return _to_json(set_default_workspace(workspace_id))


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


class ScanBody(BaseModel):
    root: str


@app.post("/api/scan")
def api_scan(body: ScanBody) -> Any:
    return _to_json(scan(Path(body.root)))


# ---------------------------------------------------------------------------
# Rename
# ---------------------------------------------------------------------------


class RenameBody(BaseModel):
    root: str
    template: str | None = None
    strict: bool = False
    directories: list[dict[str, str]] | None = None


def _build_batch(body: RenameBody) -> BatchInput | None:
    if not body.directories:
        return None
    return BatchInput(
        root=Path(body.root),
        directories=[DirectoryInput(path=Path(d["path"])) for d in body.directories],
        template=body.template,
        strict=body.strict,
    )


@app.post("/api/rename/plan")
def api_rename_plan(body: RenameBody) -> Any:
    batch = _build_batch(body)
    root = batch.root if batch else Path(body.root)
    return _to_json(
        build_rename_plan(root, batch=batch, template=body.template, strict=body.strict)
    )


@app.post("/api/rename/execute")
def api_rename_execute(body: RenameBody) -> Any:
    batch = _build_batch(body)
    root = batch.root if batch else Path(body.root)
    return _to_json(execute_rename(root, batch=batch, template=body.template, strict=body.strict))


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------


class RollbackBody(BaseModel):
    photo_dir: str


@app.post("/api/rollback/plan")
def api_rollback_plan(body: RollbackBody) -> Any:
    return _to_json(build_rollback_plan(Path(body.photo_dir)))


@app.post("/api/rollback/execute")
def api_rollback_execute(body: RollbackBody) -> Any:
    return _to_json(execute_rollback(Path(body.photo_dir)))


# ---------------------------------------------------------------------------
# Archive
# ---------------------------------------------------------------------------


class ArchiveBody(BaseModel):
    source_dir: str
    output_dir: str
    overwrite: bool = False


@app.post("/api/archive/plan")
def api_archive_plan(body: ArchiveBody) -> Any:
    return _to_json(
        build_archive_plan(Path(body.source_dir), Path(body.output_dir), overwrite=body.overwrite)
    )


@app.post("/api/archive/execute")
def api_archive_execute(body: ArchiveBody) -> Any:
    return _to_json(
        execute_archive(Path(body.source_dir), Path(body.output_dir), overwrite=body.overwrite)
    )


# ---------------------------------------------------------------------------
# Archive Name
# ---------------------------------------------------------------------------


class ArchiveNameBody(BaseModel):
    source_dir: str
    output_dir: str | None = None


@app.post("/api/archive-name")
def api_archive_name(body: ArchiveNameBody) -> Any:
    return _to_json(
        archive_name(Path(body.source_dir), Path(body.output_dir) if body.output_dir else None)
    )


# ---------------------------------------------------------------------------
# Static frontend (production build)
# ---------------------------------------------------------------------------

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/")
def serve_frontend() -> FileResponse:
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return FileResponse(FRONTEND_INDEX)
