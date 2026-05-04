from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from photograph_workflow.errors import EXIFTOOL_MISSING, METADATA_READ_FAILED


class ExifToolError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ExifToolMetadataReader:
    def __init__(self, executable: str = "exiftool"):
        self.executable = executable

    def read(self, paths: list[Path]) -> dict[Path, dict[str, Any]]:
        if not paths:
            return {}
        executable = shutil.which(self.executable)
        if not executable:
            return PythonExifMetadataReader().read(paths)
        command = [executable, "-json", "-FileType", "-Make", "-Model"]
        command.extend(
            [
                "-DateTimeOriginal",
                "-CreateDate",
                "-ModifyDate",
                "-SubSecDateTimeOriginal",
                "-SubSecCreateDate",
                "-OffsetTimeOriginal",
                "-FileName",
                "-Directory",
                "-SourceFile",
            ]
        )
        command.extend(str(path) for path in paths)
        try:
            result = subprocess.run(command, check=False, capture_output=True, text=True)
        except OSError as exc:
            raise ExifToolError(METADATA_READ_FAILED, str(exc)) from exc
        if result.returncode != 0:
            raise ExifToolError(METADATA_READ_FAILED, result.stderr.strip() or "ExifTool failed")
        try:
            records = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ExifToolError(METADATA_READ_FAILED, "ExifTool returned invalid JSON") from exc
        output: dict[Path, dict[str, Any]] = {}
        for record in records:
            source = record.get("SourceFile")
            if source:
                output[Path(str(source))] = record
        return output


class PythonExifMetadataReader:
    """Fallback metadata reader managed by Python dependencies.

    ExifTool remains the preferred reader because it understands more RAW maker
    metadata. This fallback covers the current workflow's minimum need: file
    type, make/model, and capture time for common TIFF-based RAW/DNG files.
    """

    def read(self, paths: list[Path]) -> dict[Path, dict[str, Any]]:
        try:
            import exifread
        except ImportError as exc:
            raise ExifToolError(
                EXIFTOOL_MISSING,
                "ExifTool was not found and Python fallback dependency exifread is unavailable",
            ) from exc

        output: dict[Path, dict[str, Any]] = {}
        for path in paths:
            try:
                with path.open("rb") as file_obj:
                    tags = exifread.process_file(file_obj, details=False)
            except OSError as exc:
                raise ExifToolError(METADATA_READ_FAILED, str(exc)) from exc
            output[path] = self._normalize(path, tags)
        return output

    def _normalize(self, path: Path, tags: dict[str, Any]) -> dict[str, Any]:
        def tag_value(*names: str) -> str | None:
            for name in names:
                value = tags.get(name)
                if value is not None:
                    text = str(value).strip()
                    if text:
                        return text
            return None

        file_type = path.suffix.lstrip(".").upper()
        metadata: dict[str, Any] = {
            "SourceFile": str(path),
            "FileName": path.name,
            "Directory": str(path.parent),
            "FileType": file_type,
        }
        make = tag_value("Image Make", "EXIF Make")
        model = tag_value("Image Model", "EXIF Model")
        if make:
            metadata["Make"] = make
        if model:
            metadata["Model"] = model

        datetime_original = tag_value("EXIF DateTimeOriginal")
        subsec_original = tag_value("EXIF SubSecTimeOriginal")
        if datetime_original and subsec_original:
            metadata["SubSecDateTimeOriginal"] = f"{datetime_original}.{subsec_original}"
        if datetime_original:
            metadata["DateTimeOriginal"] = datetime_original

        create_date = tag_value("EXIF DateTimeDigitized", "Image DateTime")
        if create_date:
            metadata["CreateDate"] = create_date
        modify_date = tag_value("Image DateTime")
        if modify_date:
            metadata["ModifyDate"] = modify_date
        return metadata
