from __future__ import annotations

from typing import Protocol


class ConfirmationPort(Protocol):
    def confirm(self, message: str) -> bool: ...
