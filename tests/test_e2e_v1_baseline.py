from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from src.cli.main import main
from src.ingestion.text_cleaner import clean_text
from src.reasoning.tendency_service import infer_tendency
from src.retrieval.document_builder import RetrievalDocument
from src.retrieval.retriever import VectorOnlyRetriever
from src.retrieval.vector_store_chroma import ChromaVectorStore


class _FakeApiClient:
    def __init__(self, embedding_map: dict[str, list[float]]) -> None:
        self._embedding_map = embedding_map

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embedding_map[text] for text in texts]


class _StaticRetriever:
    def __init__(self, similar_cases: list[dict[str, object]]) -> None:
        self._similar_cases = similar_cases

    def retrieve(self, query_text: str, *, top_k: int) -> list[dict[str, object]]:
        del query_text
        return self._similar_cases[:top_k]


def _workspace_tmp_dir() -> Path:
    base = Path("pytest_tmp_manual") / "step09_e2e" / uuid4().hex
    base.mkdir(parents=True, exist_ok=True)
    return base


def _build_doc(case_id: str, label: str, content: str) -> RetrievalDocument:
    return RetrievalDocument(
        doc_id=case_id,
        content=content,
        metadata={
            "case_id": case_id,
            "label": label,
            "report_time": "2024-02-12T09:15:30",
            "report_pdf_path": f"data/{label}/{case_id}/{case_id}.pdf",
            "stain_text_path": f"data/{label}/{case_id}/stain.txt",
            "image_paths": [
                f"data/{label}/{case_id}/1.jpg",
                f"data/{label}/{case_id}/2.jpg",
            ],
        },
    )


def _build_vector_retriever(tmp_path: Path) -> VectorOnlyRetriever:
    docs = [
        _build_doc("CASE-A", "HSIL", "doc-a"),
        _build_doc("CASE-B", "HSIL", "doc-b"),
        _build_doc("CASE-C", "LSIL", "doc-c"),
    ]
    embeddings = {
        "doc-a": [1.0, 0.0, 0.0],
        "doc-b": [0.8, 0.2, 0.0],
        "doc-c": [0.0, 0.0, 1.0],
        "query-hsil": [1.0, 0.0, 0.0],
    }
    vector_store = ChromaVectorStore(
        collection_name=f"step09_acc_{uuid4().hex}",
        persist_dir=tmp_path / "chroma",
    )
    retriever = VectorOnlyRetriever(
        api_client=_FakeApiClient(embeddings),
        vector_store=vector_store,
    )
    retriever.index_documents(docs)
    return retriever


def test_acc_01_valid_input_returns_top_k_similar_cases() -> None:
    retriever = _build_vector_retriever(_workspace_tmp_dir())

    results = retriever.retrieve("query-hsil", top_k=2)

    assert len(results) == 2
    assert [item["case_id"] for item in results] == ["CASE-A", "CASE-B"]
    assert results[0]["similarity"] >= results[1]["similarity"]


def test_acc_02_result_contains_traceable_evidence_and_source_fields() -> None:
    retriever = _build_vector_retriever(_workspace_tmp_dir())

    results = retriever.retrieve("query-hsil", top_k=1)
    top_hit = results[0]

    assert isinstance(top_hit["evidence"], str)
    assert top_hit["evidence"]
    assert top_hit["case_id"] == "CASE-A"
    assert top_hit["label"] == "HSIL"
    metadata = top_hit["metadata"]
    assert metadata["case_id"] == "CASE-A"
    assert metadata["label"] == "HSIL"
    assert "report_pdf_path" in metadata
    assert "stain_text_path" in metadata


def test_acc_03_cli_output_contains_tendency_reason_and_disclaimer(capsys) -> None:
    similar_cases = [
        {
            "case_id": "CASE-001",
            "label": "HSIL",
            "similarity": 0.92,
            "evidence": "sample evidence 1",
            "metadata": {"case_id": "CASE-001", "label": "HSIL"},
        },
        {
            "case_id": "CASE-002",
            "label": "HSIL",
            "similarity": 0.88,
            "evidence": "sample evidence 2",
            "metadata": {"case_id": "CASE-002", "label": "HSIL"},
        },
    ]

    exit_code = main(
        ["--stain-text", "query text", "--top-k", "2"],
        retriever_factory=lambda: _StaticRetriever(similar_cases),
        tendency_fn=infer_tendency,
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tendency"] in {"HSIL", "LSIL", "Uncertain"}
    assert isinstance(payload["reason"], str) and payload["reason"]
    assert isinstance(payload["disclaimer"], str) and payload["disclaimer"]


def test_acc_04_text_cleaning_stably_removes_del_control_char() -> None:
    dirty = "A\x7fB\x7fC"

    cleaned = clean_text(dirty)

    assert cleaned == "ABC"
    assert "\x7f" not in cleaned


def test_acc_05_insufficient_evidence_returns_uncertain() -> None:
    similar_cases = [
        {"label": "HSIL", "similarity": 0.59},
        {"label": "HSIL", "similarity": 0.57},
        {"label": "LSIL", "similarity": 0.55},
    ]

    result = infer_tendency(similar_cases, top_k=6)

    assert result["tendency"] == "Uncertain"
