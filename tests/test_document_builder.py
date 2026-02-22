from __future__ import annotations

import pytest

from src.retrieval.document_builder import (
    DocumentBuildError,
    RetrievalDocument,
    build_retrieval_document,
    build_retrieval_documents,
)


def _base_metadata_record() -> dict[str, object]:
    return {
        "case_id": "CASE-100",
        "label": "HSIL",
        "image_paths": ["data/HSIL/CASE-100/1.jpg", "data/HSIL/CASE-100/2.jpg"],
        "report_pdf_path": "data/HSIL/CASE-100/CASE-100_report_20240212091530.pdf",
        "stain_text_path": "data/HSIL/CASE-100/stain.txt",
        "report_time": "2024-02-12T09:15:30",
        "stain_text": "cells are arranged in dense clusters",
    }


def test_build_retrieval_document_without_report_text_uses_stain_text_only() -> None:
    record = _base_metadata_record()

    doc = build_retrieval_document(record)

    assert isinstance(doc, RetrievalDocument)
    assert doc.doc_id == "CASE-100"
    assert doc.content.startswith("Stain Text:\n")
    assert "cells are arranged in dense clusters" in doc.content
    assert "Report Text:" not in doc.content
    assert doc.metadata["case_id"] == "CASE-100"
    assert doc.metadata["label"] == "HSIL"
    assert doc.metadata["report_time"] == "2024-02-12T09:15:30"
    assert doc.metadata["report_pdf_path"] == record["report_pdf_path"]
    assert doc.metadata["stain_text_path"] == record["stain_text_path"]
    assert doc.metadata["image_paths"] == record["image_paths"]


def test_build_retrieval_document_with_report_text_appends_report_block() -> None:
    record = _base_metadata_record()
    record["report_text"] = "report indicates moderate to severe lesion tendency"

    doc = build_retrieval_document(record)

    assert "Stain Text:\n" in doc.content
    assert "Report Text:\n" in doc.content
    assert "report indicates moderate to severe lesion tendency" in doc.content


@pytest.mark.parametrize(
    "bad_record",
    [
        {"case_id": "CASE-100"},
        {**_base_metadata_record(), "stain_text": ""},
        {**_base_metadata_record(), "stain_text": "   "},
    ],
)
def test_build_retrieval_document_raises_for_missing_or_empty_stain_text(
    bad_record: dict[str, object],
) -> None:
    with pytest.raises(DocumentBuildError):
        build_retrieval_document(bad_record)


def test_build_retrieval_documents_preserves_input_order() -> None:
    record_a = _base_metadata_record()
    record_b = _base_metadata_record()
    record_b["case_id"] = "CASE-200"
    record_b["label"] = "LSIL"
    record_b["stain_text"] = "scattered squamous cells with mild atypia"
    record_b["report_text"] = "report suggests low-grade lesion"

    docs = build_retrieval_documents([record_a, record_b])

    assert [doc.doc_id for doc in docs] == ["CASE-100", "CASE-200"]
    assert docs[0].metadata["label"] == "HSIL"
    assert docs[1].metadata["label"] == "LSIL"
