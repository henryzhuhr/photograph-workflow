from __future__ import annotations

from pathlib import Path
from typing import Protocol


class MetadataReaderPort(Protocol):
    def read(self, paths: list[Path]) -> dict[Path, dict[str, object]]: ...
