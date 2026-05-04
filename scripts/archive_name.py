from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photograph_workflow.adapters.terminal import emit_model
from photograph_workflow.application.archive_name import archive_name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = archive_name(args.source_dir, args.output)
    emit_model(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
