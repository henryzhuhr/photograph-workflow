from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from photograph_workflow.models.plan import ArchivePlanItem


class ZipArchiveWriter:
    def write_zip(
        self,
        archive_path: Path,
        source_dir: Path,
        items: list[ArchivePlanItem],
        overwrite: bool = False,
    ) -> None:
        if archive_path.exists() and not overwrite:
            raise FileExistsError(archive_path)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as zip_file:
            for item in items:
                if not item.included:
                    continue
                arcname = Path(source_dir.name) / item.source_path.relative_to(source_dir)
                zip_file.write(item.source_path, arcname=str(arcname))
