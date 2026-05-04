from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photograph_workflow.adapters.terminal import emit_model
from photograph_workflow.application.scan import scan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    emit_model(scan(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
