from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

_TIMESTAMP_PATTERN = re.compile(r"(?P<timestamp>\d{14})(?=\.pdf$)", re.IGNORECASE)


class ReportTimeParseError(ValueError):
    """Raised when report timestamp cannot be parsed from a PDF filename."""


def parse_report_time_from_pdf_filename(pdf_filename: str | Path) -> datetime:
    file_name = Path(pdf_filename).name
    if not file_name:
        raise ReportTimeParseError("timestamp parsing failed: empty pdf filename.")

    match = _TIMESTAMP_PATTERN.search(file_name)
    if not match:
        raise ReportTimeParseError(
            f"timestamp parsing failed for {file_name}: expected 14-digit timestamp."
        )

    timestamp_token = match.group("timestamp")
    try:
        return datetime.strptime(timestamp_token, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise ReportTimeParseError(
            f"timestamp parsing failed for {file_name}: invalid timestamp value {timestamp_token}."
        ) from exc
