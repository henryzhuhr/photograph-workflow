from __future__ import annotations

from collections import defaultdict
from pathlib import Path


def duplicate_targets(targets: list[Path]) -> list[Path]:
    seen: dict[Path, int] = defaultdict(int)
    for target in targets:
        seen[target] += 1
    return [target for target, count in seen.items() if count > 1]
