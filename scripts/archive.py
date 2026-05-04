from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photograph_workflow.adapters.terminal import TerminalConfirmation, emit_model
from photograph_workflow.application.archive import build_archive_plan, execute_archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        plan = build_archive_plan(args.source_dir, args.output, overwrite=args.overwrite)
    else:
        preview = build_archive_plan(args.source_dir, args.output, overwrite=args.overwrite)
        if preview.errors:
            emit_model(preview)
            return 1
        if not args.yes and not TerminalConfirmation().confirm("Execute archive plan?"):
            emit_model(preview)
            return 1
        plan = execute_archive(args.source_dir, args.output, overwrite=args.overwrite)
    emit_model(plan)
    return 1 if plan.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
