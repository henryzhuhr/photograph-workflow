from __future__ import annotations

from pathlib import Path

from photograph_workflow.domain.extensions import is_raw_candidate, is_sidecar_candidate
from photograph_workflow.models.plan import CommonPlan


def scan(root: Path) -> CommonPlan:
    files = [path for path in root.rglob("*") if path.is_file()]
    items = []
    for path in files:
        role = (
            "raw"
            if is_raw_candidate(path)
            else "sidecar"
            if is_sidecar_candidate(path)
            else "other"
        )
        items.append({"path": path, "role": role, "extension": path.suffix})
    return CommonPlan(
        operation="scan", root=root, dry_run=True, items=items, requires_confirmation=False
    )
