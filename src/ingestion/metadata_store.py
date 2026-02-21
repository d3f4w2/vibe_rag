from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from src.ingestion.case_scanner import ScannedCase
from src.ingestion.report_time_parser import parse_report_time_from_pdf_filename
from src.models.case_record import CaseRecord


class MetadataStoreError(ValueError):
    """Raised when metadata JSONL serialization or deserialization fails."""


def build_metadata_record(
    scanned_case: ScannedCase,
    stain_text: str,
    report_text: str | None = None,
) -> dict[str, object]:
    report_time = parse_report_time_from_pdf_filename(scanned_case.report_pdf_path)
    case_record = CaseRecord(
        case_id=scanned_case.case_id,
        label=scanned_case.label,
        image_paths=list(scanned_case.image_paths),
        report_pdf_path=scanned_case.report_pdf_path,
        stain_text_path=scanned_case.stain_text_path,
        report_time=report_time,
        stain_text=stain_text,
        report_text=report_text,
    )
    return case_record.to_dict()


def write_metadata_jsonl(records: Iterable[dict[str, object]], output_path: str | Path) -> int:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    try:
        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
    except (TypeError, OSError) as exc:
        raise MetadataStoreError(f"failed to write metadata jsonl: {path}") from exc

    return count


def read_metadata_jsonl(input_path: str | Path) -> list[dict[str, object]]:
    path = Path(input_path)
    records: list[dict[str, object]] = []
    try:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                parsed = json.loads(line)
                if not isinstance(parsed, dict):
                    raise MetadataStoreError(
                        f"failed to read metadata jsonl: non-object record in {path}."
                    )
                records.append(parsed)
    except (OSError, json.JSONDecodeError) as exc:
        raise MetadataStoreError(f"failed to read metadata jsonl: {path}") from exc

    return records
