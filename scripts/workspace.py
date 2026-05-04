from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photograph_workflow.adapters.terminal import emit_model
from photograph_workflow.application.workspace import (
    add_workspace,
    list_workspaces,
    remove_workspace,
    set_default_workspace,
)
from photograph_workflow.models.photo import WorkspaceKind


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    add = sub.add_parser("add")
    add.add_argument("path", type=Path)
    add.add_argument("--name")
    add.add_argument(
        "--kind", choices=[item.value for item in WorkspaceKind], default=WorkspaceKind.CUSTOM.value
    )
    set_default = sub.add_parser("set-default")
    set_default.add_argument("workspace_id")
    remove = sub.add_parser("remove")
    remove.add_argument("workspace_id")
    args = parser.parse_args()
    if args.command == "list":
        emit_model(list_workspaces())
        return 0
    if args.command == "add":
        plan = add_workspace(args.path, name=args.name, kind=WorkspaceKind(args.kind))
    elif args.command == "set-default":
        plan = set_default_workspace(args.workspace_id)
    else:
        plan = remove_workspace(args.workspace_id)
    emit_model(plan)
    return 1 if plan.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
