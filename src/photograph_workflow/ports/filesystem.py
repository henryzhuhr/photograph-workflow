from __future__ import annotations

from pathlib import Path
from typing import Protocol


class FileSystemPort(Protocol):
    def rename(self, source: Path, target: Path) -> None: ...

    def write_json(self, path: Path, data: str) -> None: ...

    def read_text(self, path: Path) -> str: ...
