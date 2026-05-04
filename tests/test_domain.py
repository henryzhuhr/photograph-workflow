from __future__ import annotations

from datetime import datetime

import pytest

from photograph_workflow.domain.metadata_reader import capture_time, is_dji_dng
from photograph_workflow.domain.naming_template import (
    TemplateError,
    render_template,
    title_from_directory_name,
)


def test_render_default_template_tokens() -> None:
    result = render_template(
        "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}",
        folder="20260101-上海东方明珠",
        parent="Shanghai",
        relative_dir="Travel/Shanghai/20260101-上海东方明珠",
        title="上海东方明珠",
        date=datetime(2026, 1, 1, 8, 0, 1),
        original="DSC00000",
    )
    assert result == "20260101-上海东方明珠-080001_DSC00000"


def test_render_rejects_unsupported_token() -> None:
    with pytest.raises(TemplateError):
        render_template(
            "{camera}",
            folder="folder",
            parent="parent",
            relative_dir="folder",
            title="title",
            date=datetime(2026, 1, 1, 8, 0, 1),
            original="DSC00000",
        )


def test_title_from_directory_name_strips_date_prefix() -> None:
    assert title_from_directory_name("20260101-HongKong_Victoria_Peak") == "HongKong_Victoria_Peak"


def test_capture_time_priority_and_dji_detection() -> None:
    metadata = {
        "FileType": "DNG",
        "Make": "DJI",
        "CreateDate": "2026:01:01 08:00:02",
        "DateTimeOriginal": "2026:01:01 08:00:01",
    }
    assert is_dji_dng(metadata)
    assert capture_time(metadata) == datetime(2026, 1, 1, 8, 0, 1)
