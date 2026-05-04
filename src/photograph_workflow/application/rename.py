from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from photograph_workflow.adapters.filesystem_local import LocalFileSystem
from photograph_workflow.adapters.metadata_exiftool import (
    ExifToolError,
    ExifToolMetadataReader,
)
from photograph_workflow.config import DEFAULT_RENAME_TEMPLATE
from photograph_workflow.domain.conflicts import duplicate_targets
from photograph_workflow.domain.extensions import (
    is_dng,
    is_raw_candidate,
    is_supported_arw,
)
from photograph_workflow.domain.metadata_reader import capture_time, is_dji_dng
from photograph_workflow.domain.metadata_record import (
    dump_metadata,
    metadata_path,
    now_metadata_file,
    read_metadata_file,
)
from photograph_workflow.domain.naming_template import (
    TemplateError,
    render_template,
    title_from_directory_name,
)
from photograph_workflow.domain.sanitize import is_valid_filename
from photograph_workflow.domain.sidecar import match_sidecars
from photograph_workflow.errors import (
    CAPTURE_TIME_MISSING,
    DIRECTORY_NO_SUPPORTED_SOURCES,
    EXIFTOOL_MISSING,
    INVALID_FILENAME,
    METADATA_DEVIATION,
    METADATA_WRITE_FAILED,
    SIDECAR_AMBIGUOUS,
    TARGET_CONFLICT,
    TARGET_EXISTS,
    UNSUPPORTED_DNG_SOURCE,
)
from photograph_workflow.models.input import BatchInput, DirectoryInput
from photograph_workflow.models.metadata import MetadataFile, MetadataFileEntry
from photograph_workflow.models.photo import DirectoryStatus, FileRole, FileStatus
from photograph_workflow.models.plan import PlanIssue, RenamePlan, RenamePlanItem
from photograph_workflow.ports.clock import ClockPort, SystemClock
from photograph_workflow.ports.filesystem import FileSystemPort
from photograph_workflow.ports.metadata_reader import MetadataReaderPort


def _directories_from_input(
    root: Path, batch: BatchInput | None
) -> list[tuple[Path, DirectoryInput | None]]:
    if not batch:
        return [(root, None)]
    return [(batch.root / item.path, item) for item in batch.directories]


def _all_files(directories: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for directory in directories:
        for path in directory.rglob("*"):
            if path.is_file() and path not in seen:
                files.append(path)
                seen.add(path)
    return files


def _entry_for(metadata: MetadataFile | None, name: str) -> MetadataFileEntry | None:
    if not metadata:
        return None
    for entry in metadata.files:
        if name in {entry.current_name, entry.original_name, entry.planned_name}:
            return entry
    return None


def _title_and_template(
    directory: Path,
    metadata: MetadataFile | None,
    config: DirectoryInput | None,
    root_template: str | None,
) -> tuple[str, str]:
    title = (
        config.title
        if config and config.title
        else metadata.title
        if metadata and metadata.title
        else title_from_directory_name(directory.name)
    )
    template = (
        config.template
        if config and config.template
        else metadata.template
        if metadata and metadata.template
        else root_template or DEFAULT_RENAME_TEMPLATE
    )
    return title, template


def build_rename_plan(
    root: Path,
    *,
    batch: BatchInput | None = None,
    template: str | None = None,
    strict: bool = False,
    metadata_reader: MetadataReaderPort | None = None,
) -> RenamePlan:
    actual_root = batch.root if batch else root
    directory_configs = _directories_from_input(actual_root, batch)
    directories = [directory for directory, _config in directory_configs]
    root_template = batch.template if batch and batch.template else template
    strict_mode = batch.strict if batch else strict
    files = _all_files(directories)
    raw_candidates = [path for path in files if is_raw_candidate(path)]
    warnings: list[PlanIssue] = []
    errors: list[PlanIssue] = []

    reader = metadata_reader or ExifToolMetadataReader()
    try:
        metadata_map = reader.read(raw_candidates)
    except ExifToolError as exc:
        code = exc.code or EXIFTOOL_MISSING
        errors.append(PlanIssue(code=code, message=exc.message, path=actual_root))
        return RenamePlan(
            root=actual_root,
            dry_run=True,
            items=[],
            warnings=warnings,
            errors=errors,
            metadata_changes=[],
            requires_confirmation=True,
        )

    supported_raws: list[Path] = []
    for path in raw_candidates:
        metadata = metadata_map.get(path, {})
        if is_supported_arw(path):
            supported_raws.append(path)
        elif is_dng(path) and is_dji_dng(metadata):
            supported_raws.append(path)
        elif is_dng(path):
            issue = PlanIssue(
                code=UNSUPPORTED_DNG_SOURCE,
                message="DNG source is not confirmed as DJI",
                path=path,
            )
            warnings.append(issue)

    if not supported_raws:
        issue = PlanIssue(
            code=DIRECTORY_NO_SUPPORTED_SOURCES,
            message="No supported RAW/DNG files found",
            path=actual_root,
        )
        (errors if strict_mode else warnings).append(issue)

    sidecar_matches, ambiguous = match_sidecars(supported_raws, files)
    for stem in sorted(ambiguous):
        errors.append(
            PlanIssue(
                code=SIDECAR_AMBIGUOUS,
                message="Multiple RAW/DNG files share one stem",
                details={"stem": stem},
            )
        )

    metadata_by_dir: dict[Path, MetadataFile | None] = {}
    config_by_dir: dict[Path, DirectoryInput | None] = {}
    for directory, config in directory_configs:
        config_by_dir[directory] = config
    for raw in supported_raws:
        metadata, issue = read_metadata_file(raw.parent)
        metadata_by_dir[raw.parent] = metadata
        if issue:
            errors.append(issue)

    items: list[RenamePlanItem] = []
    metadata_changes: list[dict[str, object]] = []

    for raw in supported_raws:
        raw_metadata = metadata_map.get(raw, {})
        captured_at = capture_time(raw_metadata)
        if not captured_at:
            errors.append(
                PlanIssue(
                    code=CAPTURE_TIME_MISSING,
                    message="RAW/DNG capture time is missing; file may be damaged or unsupported",
                    path=raw,
                )
            )
            continue
        metadata = metadata_by_dir.get(raw.parent)
        config = config_by_dir.get(raw.parent)
        title, actual_template = _title_and_template(raw.parent, metadata, config, root_template)
        entry = _entry_for(metadata, raw.name)
        original_name = entry.original_name if entry else raw.name
        try:
            new_stem = render_template(
                actual_template,
                folder=raw.parent.name,
                parent=raw.parent.parent.name,
                relative_dir=str(raw.parent.relative_to(actual_root))
                if raw.parent.is_relative_to(actual_root)
                else raw.parent.name,
                title=title,
                date=captured_at,
                original=Path(original_name).stem,
            )
        except TemplateError as exc:
            errors.append(PlanIssue(code=INVALID_FILENAME, message=str(exc), path=raw))
            continue
        target_name = f"{new_stem}{raw.suffix}"
        if not is_valid_filename(target_name):
            errors.append(
                PlanIssue(
                    code=INVALID_FILENAME,
                    message="Generated filename is invalid",
                    path=raw,
                    details={"target": target_name},
                )
            )
            continue
        target = raw.with_name(target_name)
        items.append(
            RenamePlanItem(
                source_path=raw,
                target_path=target,
                role=FileRole.RAW,
                raw_source_path=None,
                original_name=original_name,
                current_name=raw.name,
                planned_name=target.name,
                status=FileStatus.PENDING,
            )
        )
        for sidecar in sidecar_matches.get(raw, []):
            side_entry = _entry_for(metadata, sidecar.name)
            side_original_name = side_entry.original_name if side_entry else sidecar.name
            side_target = sidecar.with_name(f"{new_stem}{sidecar.suffix}")
            items.append(
                RenamePlanItem(
                    source_path=sidecar,
                    target_path=side_target,
                    role=FileRole.SIDECAR,
                    raw_source_path=raw,
                    original_name=side_original_name,
                    current_name=sidecar.name,
                    planned_name=side_target.name,
                    status=FileStatus.PENDING,
                )
            )

    for target in duplicate_targets([item.target_path for item in items]):
        errors.append(
            PlanIssue(
                code=TARGET_CONFLICT, message="Multiple files target the same path", path=target
            )
        )
    planned_sources = {item.source_path for item in items}
    for item in items:
        if item.target_path.exists() and item.target_path not in planned_sources:
            errors.append(
                PlanIssue(
                    code=TARGET_EXISTS,
                    message="Target exists outside the plan",
                    path=item.target_path,
                )
            )

    for directory, metadata in metadata_by_dir.items():
        if not metadata:
            continue
        current_names = {path.name for path in files if path.parent == directory}
        for entry in metadata.files:
            if entry.current_name not in current_names and entry.planned_name not in current_names:
                errors.append(
                    PlanIssue(
                        code=METADATA_DEVIATION,
                        message="Metadata entry does not match current filesystem state",
                        path=directory / entry.current_name,
                    )
                )

    for directory in sorted({item.source_path.parent for item in items}):
        metadata_changes.append(
            {"path": metadata_path(directory), "status": DirectoryStatus.PENDING}
        )

    return RenamePlan(
        root=actual_root,
        dry_run=True,
        items=items,
        warnings=warnings,
        errors=errors,
        metadata_changes=metadata_changes,
        requires_confirmation=True,
    )


def execute_rename(
    root: Path,
    *,
    batch: BatchInput | None = None,
    template: str | None = None,
    strict: bool = False,
    metadata_reader: MetadataReaderPort | None = None,
    filesystem: FileSystemPort | None = None,
    clock: ClockPort | None = None,
) -> RenamePlan:
    plan = build_rename_plan(
        root, batch=batch, template=template, strict=strict, metadata_reader=metadata_reader
    )
    plan.dry_run = False
    if plan.errors:
        return plan
    fs = filesystem or LocalFileSystem()
    now = (clock or SystemClock()).now()
    by_dir: dict[Path, list[RenamePlanItem]] = defaultdict(list)
    for item in plan.items:
        by_dir[item.source_path.parent].append(item)

    try:
        for directory, items in by_dir.items():
            metadata, _issue = read_metadata_file(directory)
            if not metadata:
                metadata = now_metadata_file(
                    title_from_directory_name(directory.name),
                    template or DEFAULT_RENAME_TEMPLATE,
                    now,
                )
            metadata.status = DirectoryStatus.PENDING
            metadata.updated_at = now
            entries_by_original = {entry.original_name: entry for entry in metadata.files}
            for item in items:
                entry = entries_by_original.get(item.original_name)
                if not entry:
                    metadata.files.append(
                        MetadataFileEntry(
                            original_name=item.original_name,
                            current_name=item.current_name,
                            planned_name=item.planned_name,
                            role=item.role,
                            status=FileStatus.PENDING,
                        )
                    )
                else:
                    entry.current_name = item.current_name
                    entry.planned_name = item.planned_name
                    entry.status = FileStatus.PENDING
            fs.write_json(metadata_path(directory), dump_metadata(metadata))

        for item in plan.items:
            if item.source_path != item.target_path:
                fs.rename(item.source_path, item.target_path)

        for directory, items in by_dir.items():
            metadata, _issue = read_metadata_file(directory)
            if not metadata:
                continue
            metadata.status = DirectoryStatus.RENAMED
            metadata.updated_at = now
            by_original = {entry.original_name: entry for entry in metadata.files}
            for item in items:
                entry = by_original[item.original_name]
                entry.current_name = item.target_path.name
                entry.planned_name = None
                entry.status = FileStatus.RENAMED
            fs.write_json(metadata_path(directory), dump_metadata(metadata))
    except OSError as exc:
        plan.errors.append(PlanIssue(code=METADATA_WRITE_FAILED, message=str(exc), path=root))
    return plan
