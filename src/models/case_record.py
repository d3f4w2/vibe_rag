from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

AllowedLabel = Literal["HSIL", "LSIL"]
_ALLOWED_LABELS = {"HSIL", "LSIL"}


class CaseRecordValidationError(ValueError):
    """Raised when case metadata does not satisfy the schema contract."""


def _require_non_empty_string(field_name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CaseRecordValidationError(
            f"{field_name} is required and must be a non-empty string."
        )


def _require_non_empty_string_list(field_name: str, value: list[str] | None) -> None:
    if not isinstance(value, list) or len(value) == 0:
        raise CaseRecordValidationError(
            f"{field_name} is required and must be a non-empty list of strings."
        )

    for idx, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise CaseRecordValidationError(
                f"{field_name}[{idx}] must be a non-empty string."
            )


def _require_datetime(field_name: str, value: datetime | None) -> None:
    if not isinstance(value, datetime):
        raise CaseRecordValidationError(
            f"{field_name} is required and must be a datetime object."
        )


@dataclass
class CaseRecord:
    case_id: str | None = None
    label: AllowedLabel | None = None
    image_paths: list[str] | None = None
    report_pdf_path: str | None = None
    stain_text_path: str | None = None
    report_time: datetime | None = None
    stain_text: str | None = None
    report_text: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string("case_id", self.case_id)
        self._validate_label(self.label)
        _require_non_empty_string_list("image_paths", self.image_paths)
        _require_non_empty_string("report_pdf_path", self.report_pdf_path)
        _require_non_empty_string("stain_text_path", self.stain_text_path)
        _require_datetime("report_time", self.report_time)

        _require_non_empty_string("stain_text", self.stain_text)

        if self.report_text is not None and not isinstance(self.report_text, str):
            raise CaseRecordValidationError(
                "report_text must be a string when provided."
            )

    @staticmethod
    def _validate_label(label: str | None) -> None:
        if label not in _ALLOWED_LABELS:
            allowed = ", ".join(sorted(_ALLOWED_LABELS))
            raise CaseRecordValidationError(
                f"label must be one of: {allowed}; got: {label!r}"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "label": self.label,
            "image_paths": list(self.image_paths),
            "report_pdf_path": self.report_pdf_path,
            "stain_text_path": self.stain_text_path,
            "report_time": self.report_time.isoformat(),
            "stain_text": self.stain_text,
            "report_text": self.report_text,
        }
