from __future__ import annotations

from pydantic import BaseModel


class TerminalConfirmation:
    def confirm(self, message: str) -> bool:
        answer = input(f"{message} [y/N] ").strip().lower()
        return answer in {"y", "yes"}


def render_model(model: BaseModel) -> str:
    return model.model_dump_json(indent=2)


def emit_model(model: BaseModel) -> None:
    try:
        print(render_model(model))
    except BrokenPipeError:
        raise SystemExit(0) from None
