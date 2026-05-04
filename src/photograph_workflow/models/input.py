from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator, model_validator

from .base import WorkflowModel
from .photo import WorkspaceKind


class DirectoryInput(WorkflowModel):
    path: Path
    title: str | None = None
    template: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("title cannot be blank")
        return value

    @field_validator("path")
    @classmethod
    def path_must_be_relative(cls, value: Path) -> Path:
        if value.is_absolute() or ".." in value.parts:
            raise ValueError("directory path must be relative and cannot contain '..'")
        return value


class BatchInput(WorkflowModel):
    root: Path
    directories: list[DirectoryInput] = Field(min_length=1)
    template: str | None = None
    strict: bool = False

    @field_validator("root")
    @classmethod
    def root_must_exist(cls, value: Path) -> Path:
        if not value.exists() or not value.is_dir():
            raise ValueError("root must exist and be a directory")
        return value

    @model_validator(mode="after")
    def directories_must_exist(self) -> BatchInput:
        for item in self.directories:
            target = self.root / item.path
            if not target.exists() or not target.is_dir():
                raise ValueError(f"directory does not exist: {item.path}")
        return self


class WorkspaceCommandInput(WorkflowModel):
    operation: str
    path: Path | None = None
    name: str | None = None
    kind: WorkspaceKind = WorkspaceKind.CUSTOM
    workspace_id: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("name cannot be blank")
        return value
