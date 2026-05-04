from __future__ import annotations

from pathlib import Path

from photograph_workflow.application.rename import build_rename_plan, execute_rename
from photograph_workflow.application.rollback import (
    build_rollback_plan,
    execute_rollback,
)


class FakeMetadataReader:
    def __init__(self, metadata: dict[Path, dict[str, object]]):
        self.metadata = metadata

    def read(self, paths: list[Path]) -> dict[Path, dict[str, object]]:
        return {path: self.metadata[path] for path in paths if path in self.metadata}


def test_rename_dry_run_matches_raw_and_sidecar(tmp_path: Path) -> None:
    photo_dir = tmp_path / "20260101-上海东方明珠"
    photo_dir.mkdir()
    raw = photo_dir / "DSC00000.ARW"
    sidecar = photo_dir / "DSC00000.XMP"
    raw.write_bytes(b"raw")
    sidecar.write_text("xmp", encoding="utf-8")
    reader = FakeMetadataReader(
        {raw: {"FileType": "ARW", "DateTimeOriginal": "2026:01:01 08:00:01"}}
    )

    plan = build_rename_plan(tmp_path, metadata_reader=reader)

    assert not plan.errors
    assert {item.target_path.name for item in plan.items} == {
        "20260101-上海东方明珠-080001_DSC00000.ARW",
        "20260101-上海东方明珠-080001_DSC00000.XMP",
    }


def test_rename_execute_writes_metadata_and_rollback_restores(tmp_path: Path) -> None:
    photo_dir = tmp_path / "20260101-上海东方明珠"
    photo_dir.mkdir()
    raw = photo_dir / "DSC00000.ARW"
    raw.write_bytes(b"raw")
    reader = FakeMetadataReader(
        {raw: {"FileType": "ARW", "DateTimeOriginal": "2026:01:01 08:00:01"}}
    )

    rename_plan = execute_rename(tmp_path, metadata_reader=reader)

    assert not rename_plan.errors
    renamed = photo_dir / "20260101-上海东方明珠-080001_DSC00000.ARW"
    assert renamed.exists()
    assert (photo_dir / ".metadata.json").exists()

    rollback_plan = build_rollback_plan(photo_dir)
    assert not rollback_plan.errors

    executed = execute_rollback(photo_dir)
    assert not executed.errors
    assert raw.exists()
