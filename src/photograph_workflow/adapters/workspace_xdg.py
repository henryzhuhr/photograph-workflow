from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from photograph_workflow.config import (
    WORKSPACE_DATA_DIR,
    WORKSPACE_FILENAME,
    WORKSPACE_VERSION,
)
from photograph_workflow.models.metadata import WorkspaceFile


def default_workspace_path() -> Path:
    data_home = Path.home() / ".local" / "share"
    return data_home / WORKSPACE_DATA_DIR / WORKSPACE_FILENAME


class XdgWorkspaceResolver:
    def __init__(self, path: Path | None = None):
        self.path = path or default_workspace_path()

    def load(self) -> WorkspaceFile:
        if not self.path.exists():
            now = datetime.now().astimezone()
            return WorkspaceFile(version=WORKSPACE_VERSION, created_at=now, updated_at=now)
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return WorkspaceFile.model_validate(payload)

    def save(self, workspace_file: WorkspaceFile) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(workspace_file.model_dump_json(indent=2) + "\n", encoding="utf-8")

    def list(self):
        return self.load().workspaces
