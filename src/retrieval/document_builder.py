from __future__ import annotations

from dataclasses import dataclass


class DocumentBuildError(ValueError):
    """Raised when a metadata record cannot be converted to a retrieval document."""


@dataclass(frozen=True)
class RetrievalDocument:
    doc_id: str
    content: str
    metadata: dict[str, object]


_REQUIRED_METADATA_STRING_FIELDS = (
    "case_id",
    "label",
    "report_time",
    "report_pdf_path",
    "stain_text_path",
)


def _require_non_empty_string(record: dict[str, object], field_name: str) -> str:
    value = record.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise DocumentBuildError(
            f"{field_name} is required and must be a non-empty string."
        )
    return value


def _require_string_list(record: dict[str, object], field_name: str) -> list[str]:
    value = record.get(field_name)
    if not isinstance(value, list) or len(value) == 0:
        raise DocumentBuildError(
            f"{field_name} is required and must be a non-empty list of strings."
        )

    normalized: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise DocumentBuildError(f"{field_name}[{idx}] must be a non-empty string.")
        normalized.append(item)
    return normalized


def _normalize_optional_report_text(record: dict[str, object]) -> str | None:
    report_text = record.get("report_text")
    if report_text is None:
        return None
    if not isinstance(report_text, str):
        raise DocumentBuildError("report_text must be a string when provided.")
    if not report_text.strip():
        return None
    return report_text


def _build_metadata(record: dict[str, object]) -> dict[str, object]:
    metadata = {
        field_name: _require_non_empty_string(record, field_name)
        for field_name in _REQUIRED_METADATA_STRING_FIELDS
    }
    metadata["image_paths"] = _require_string_list(record, "image_paths")
    return metadata


def _build_content(stain_text: str, report_text: str | None) -> str:
    content = f"Stain Text:\n{stain_text}"
    if report_text is not None:
        content += f"\n\nReport Text:\n{report_text}"
    return content


def build_retrieval_document(record: dict[str, object]) -> RetrievalDocument:
    if not isinstance(record, dict):
        raise DocumentBuildError("record must be a dict.")

    stain_text = _require_non_empty_string(record, "stain_text")
    report_text = _normalize_optional_report_text(record)
    metadata = _build_metadata(record)

    content = _build_content(stain_text, report_text)

    return RetrievalDocument(
        doc_id=metadata["case_id"],
        content=content,
        metadata=metadata,
    )


def build_retrieval_documents(records: list[dict[str, object]]) -> list[RetrievalDocument]:
    if not isinstance(records, list):
        raise DocumentBuildError("records must be a list of metadata records.")
    return [build_retrieval_document(record) for record in records]
