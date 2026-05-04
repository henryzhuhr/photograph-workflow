from __future__ import annotations

from enum import StrEnum


class FileRole(StrEnum):
    RAW = "raw"
    SIDECAR = "sidecar"
    OTHER = "other"


class SourceFileType(StrEnum):
    SONY_ARW = "sony_arw"
    DJI_DNG = "dji_dng"


class SidecarFileType(StrEnum):
    ADOBE_XMP = "adobe_xmp"
    ADOBE_ACR = "adobe_acr"
    CAMERA_JPEG = "camera_jpeg"


class DirectoryStatus(StrEnum):
    CONFIGURED = "configured"
    PENDING = "pending"
    RENAMED = "renamed"
    ROLLED_BACK = "rolled_back"


class FileStatus(StrEnum):
    PENDING = "pending"
    RENAMED = "renamed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class WorkspaceKind(StrEnum):
    LOCAL = "local"
    ICLOUD = "icloud"
    CUSTOM = "custom"
