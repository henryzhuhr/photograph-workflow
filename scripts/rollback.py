from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photograph_workflow.adapters.terminal import TerminalConfirmation, emit_model
from photograph_workflow.application.rollback import (
    build_rollback_plan,
    execute_rollback,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("photo_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        plan = build_rollback_plan(args.photo_dir)
    else:
        preview = build_rollback_plan(args.photo_dir)
        if preview.errors:
            emit_model(preview)
            return 1
        if not args.yes and not TerminalConfirmation().confirm("Execute rollback plan?"):
            emit_model(preview)
            return 1
        plan = execute_rollback(args.photo_dir)
    emit_model(plan)
    return 1 if plan.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
