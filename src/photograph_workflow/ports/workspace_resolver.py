from __future__ import annotations

from typing import Protocol

from photograph_workflow.models.metadata import WorkspaceEntry, WorkspaceFile


class WorkspaceResolverPort(Protocol):
    def load(self) -> WorkspaceFile: ...

    def save(self, workspace_file: WorkspaceFile) -> None: ...

    def list(self) -> list[WorkspaceEntry]: ...
