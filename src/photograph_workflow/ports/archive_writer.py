from __future__ import annotations

from pathlib import Path
from typing import Protocol

from photograph_workflow.models.plan import ArchivePlanItem


class ArchiveWriterPort(Protocol):
    def write_zip(
        self,
        archive_path: Path,
        source_dir: Path,
        items: list[ArchivePlanItem],
        overwrite: bool = False,
    ) -> None: ...
