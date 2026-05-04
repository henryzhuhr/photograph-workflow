from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .extensions import is_sidecar_candidate


def match_sidecars(
    raw_paths: list[Path], all_files: list[Path]
) -> tuple[dict[Path, list[Path]], set[str]]:
    by_dir_stem: dict[tuple[Path, str], list[Path]] = defaultdict(list)
    for raw in raw_paths:
        by_dir_stem[(raw.parent, raw.stem)].append(raw)

    ambiguous = {stem for (_directory, stem), paths in by_dir_stem.items() if len(paths) > 1}
    matches: dict[Path, list[Path]] = {raw: [] for raw in raw_paths}
    sidecars = [path for path in all_files if is_sidecar_candidate(path)]
    raw_lookup = {(raw.parent, raw.stem): raw for raw in raw_paths if raw.stem not in ambiguous}
    for sidecar in sidecars:
        raw = raw_lookup.get((sidecar.parent, sidecar.stem))
        if raw:
            matches[raw].append(sidecar)
    return matches, ambiguous
