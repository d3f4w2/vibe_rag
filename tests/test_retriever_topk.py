from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from src.retrieval.document_builder import RetrievalDocument
from src.retrieval.retriever import VectorOnlyRetriever
from src.retrieval.vector_store_chroma import ChromaVectorStore


class _FakeApiClient:
    def __init__(self, embedding_map: dict[str, list[float]]) -> None:
        self._embedding_map = embedding_map

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embedding_map[text] for text in texts]


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


def _build_retriever(tmp_path: Path) -> VectorOnlyRetriever:
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

    collection_name = f"test_step06_{uuid4().hex}"
    vector_store = ChromaVectorStore(
        collection_name=collection_name,
        persist_dir=tmp_path / "chroma",
    )
    retriever = VectorOnlyRetriever(
        api_client=_FakeApiClient(embeddings),
        vector_store=vector_store,
    )
    retriever.index_documents(docs)
    return retriever


def _workspace_tmp_dir() -> Path:
    base = Path("pytest_tmp_manual") / "step06_retriever" / uuid4().hex
    base.mkdir(parents=True, exist_ok=True)
    return base


def test_retrieve_top_k_returns_expected_count_and_similarity_order() -> None:
    retriever = _build_retriever(_workspace_tmp_dir())

    results = retriever.retrieve("query-hsil", top_k=2)

    assert len(results) == 2
    assert [item["case_id"] for item in results] == ["CASE-A", "CASE-B"]
    assert results[0]["similarity"] >= results[1]["similarity"]


def test_retrieve_top_k_includes_similarity_and_source_metadata() -> None:
    retriever = _build_retriever(_workspace_tmp_dir())

    results = retriever.retrieve("query-hsil", top_k=3)

    assert len(results) == 3
    first = results[0]
    assert first["case_id"] == "CASE-A"
    assert first["label"] == "HSIL"
    assert isinstance(first["similarity"], float)
    assert first["evidence"] == "doc-a"

    metadata = first["metadata"]
    assert metadata["case_id"] == "CASE-A"
    assert metadata["label"] == "HSIL"
    assert "report_pdf_path" in metadata
    assert "stain_text_path" in metadata
