from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PostProcessorProfile:
    name: str
    sidecar_extensions: tuple[str, ...]
    same_stem_required: bool = True


LIGHTROOM_PROFILE = PostProcessorProfile(
    name="lightroom",
    sidecar_extensions=(".xmp", ".acr", ".jpg", ".jpeg"),
)
