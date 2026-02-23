from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from src.retrieval.document_builder import RetrievalDocument
from src.retrieval.vector_store_chroma import ChromaVectorStore


def _workspace_tmp_dir() -> Path:
    base = Path("pytest_tmp_manual") / "step13_vector_store" / uuid4().hex
    base.mkdir(parents=True, exist_ok=True)
    return base


def test_query_restores_non_scalar_metadata_fields() -> None:
    vector_store = ChromaVectorStore(
        collection_name=f"step13_meta_{uuid4().hex}",
        persist_dir=_workspace_tmp_dir() / "chroma",
    )
    document = RetrievalDocument(
        doc_id="CASE-META-001",
        content="sample evidence",
        metadata={
            "case_id": "CASE-META-001",
            "label": "HSIL",
            "report_pdf_path": "data/HSIL/CASE-META-001/report.pdf",
            "stain_text_path": "data/HSIL/CASE-META-001/stain.txt",
            "image_paths": ["data/HSIL/CASE-META-001/1.jpg", "data/HSIL/CASE-META-001/2.jpg"],
            "extra": {"source": "unit-test", "version": 1},
        },
    )

    vector_store.upsert_documents([document], [[0.1, 0.2, 0.3]])
    results = vector_store.query(query_embedding=[0.1, 0.2, 0.3], top_k=1)

    assert len(results) == 1
    metadata = results[0]["metadata"]
    assert metadata["image_paths"] == [
        "data/HSIL/CASE-META-001/1.jpg",
        "data/HSIL/CASE-META-001/2.jpg",
    ]
    assert metadata["extra"] == {"source": "unit-test", "version": 1}
    assert "rag_encoded_json_keys" not in metadata
    assert "__rag_encoded_json_keys" not in metadata


def test_restore_is_backward_compatible_with_legacy_marker_key() -> None:
    restored = ChromaVectorStore._restore_metadata_from_chroma(
        {
            "case_id": "CASE-META-LEGACY",
            "__rag_encoded_json_keys": "[\"image_paths\"]",
            "image_paths": "[\"legacy-a.jpg\",\"legacy-b.jpg\"]",
        }
    )

    assert restored["case_id"] == "CASE-META-LEGACY"
    assert restored["image_paths"] == ["legacy-a.jpg", "legacy-b.jpg"]
