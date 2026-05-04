from __future__ import annotations

from pathlib import Path


class LocalFileSystem:
    def rename(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)

    def write_json(self, path: Path, data: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")

    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def recursive_files(self, root: Path) -> list[Path]:
        return [path for path in root.rglob("*") if path.is_file()]
