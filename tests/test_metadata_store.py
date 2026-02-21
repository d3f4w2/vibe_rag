from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from src.ingestion.case_scanner import ScannedCase
from src.ingestion.metadata_store import (
    build_metadata_record,
    read_metadata_jsonl,
    write_metadata_jsonl,
)
from src.ingestion.report_time_parser import (
    ReportTimeParseError,
    parse_report_time_from_pdf_filename,
)


def test_parse_report_time_from_pdf_filename_parses_yyyymmddhhmmss() -> None:
    filename = "CASE-001_检查报告_20240212091530.pdf"

    parsed = parse_report_time_from_pdf_filename(filename)

    assert parsed == datetime(2024, 2, 12, 9, 15, 30)


def test_parse_report_time_from_pdf_filename_raises_diagnostic_error() -> None:
    filename = "CASE-001_检查报告_20241312091530.pdf"

    with pytest.raises(ReportTimeParseError) as exc_info:
        parse_report_time_from_pdf_filename(filename)

    error_text = str(exc_info.value)
    assert "timestamp" in error_text.lower()
    assert filename in error_text


def test_metadata_jsonl_roundtrip_contains_required_fields(tmp_path: Path) -> None:
    scanned_case = ScannedCase(
        case_id="CASE-001",
        label="HSIL",
        case_dir=str(tmp_path / "HSIL" / "CASE-001"),
        image_paths=[str(tmp_path / "HSIL" / "CASE-001" / f"{i}.jpg") for i in range(1, 6)],
        report_pdf_path=str(
            tmp_path
            / "HSIL"
            / "CASE-001"
            / "CASE-001_检查报告_20240212091530.pdf"
        ),
        stain_text_path=str(tmp_path / "HSIL" / "CASE-001" / "着色情况.txt"),
    )
    metadata_path = tmp_path / "metadata.jsonl"

    record = build_metadata_record(
        scanned_case=scanned_case,
        stain_text="sample stain text",
        report_text="sample report text",
    )
    written_count = write_metadata_jsonl([record], metadata_path)
    loaded_records = read_metadata_jsonl(metadata_path)

    assert written_count == 1
    assert len(loaded_records) == 1

    loaded = loaded_records[0]
    assert set(loaded.keys()) == {
        "case_id",
        "label",
        "image_paths",
        "report_pdf_path",
        "stain_text_path",
        "report_time",
        "stain_text",
        "report_text",
    }
    assert loaded["case_id"] == "CASE-001"
    assert loaded["label"] == "HSIL"
    assert loaded["report_time"] == "2024-02-12T09:15:30"
    assert loaded["stain_text"] == "sample stain text"
    assert loaded["report_text"] == "sample report text"
