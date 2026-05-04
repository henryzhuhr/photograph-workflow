from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photograph_workflow.adapters.terminal import TerminalConfirmation, emit_model
from photograph_workflow.application.rename import build_rename_plan, execute_rename
from photograph_workflow.models.input import BatchInput


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--template")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    batch = None
    root = args.root
    if args.input:
        batch = BatchInput.model_validate(json.loads(args.input.read_text(encoding="utf-8")))
        root = batch.root
    if not root:
        parser.error("root is required unless --input is provided")

    if args.dry_run:
        plan = build_rename_plan(root, batch=batch, template=args.template, strict=args.strict)
    else:
        preview = build_rename_plan(root, batch=batch, template=args.template, strict=args.strict)
        if preview.errors:
            emit_model(preview)
            return 1
        if not args.yes and not TerminalConfirmation().confirm("Execute rename plan?"):
            emit_model(preview)
            return 1
        plan = execute_rename(root, batch=batch, template=args.template, strict=args.strict)
    emit_model(plan)
    return 1 if plan.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
