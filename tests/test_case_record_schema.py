from datetime import datetime

import pytest

from src.models.case_record import CaseRecord, CaseRecordValidationError


def _valid_payload() -> dict:
    return {
        "case_id": "CASE-001",
        "label": "HSIL",
        "image_paths": ["data/HSIL/CASE-001/1.jpg"],
        "report_pdf_path": "data/HSIL/CASE-001/CASE-001_report_20240212091530.pdf",
        "stain_text_path": "data/HSIL/CASE-001/stain.txt",
        "report_time": datetime(2024, 2, 12, 9, 15, 30),
        "stain_text": "example stain text",
        "report_text": "optional report text",
    }


def test_case_record_requires_mandatory_fields() -> None:
    payload = _valid_payload()
    payload.pop("case_id")

    with pytest.raises(CaseRecordValidationError) as exc_info:
        CaseRecord(**payload)

    assert "case_id" in str(exc_info.value)


def test_case_record_requires_report_time() -> None:
    payload = _valid_payload()
    payload.pop("report_time")

    with pytest.raises(CaseRecordValidationError) as exc_info:
        CaseRecord(**payload)

    assert "report_time" in str(exc_info.value)


def test_case_record_rejects_invalid_label() -> None:
    payload = _valid_payload()
    payload["label"] = "ASCUS"

    with pytest.raises(CaseRecordValidationError) as exc_info:
        CaseRecord(**payload)

    assert "label" in str(exc_info.value)
    assert "HSIL" in str(exc_info.value)
    assert "LSIL" in str(exc_info.value)
