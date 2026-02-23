from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from src.infra.api_client import ApiTimeoutError
from src.retrieval.document_builder import RetrievalDocument
from src.retrieval.langchain_retriever import LangChainRetriever
from src.retrieval.retriever import RetrieverError, build_default_vector_only_retriever


class _FakeApiClient:
    def __init__(self, embedding_map: dict[str, list[float]]) -> None:
        self._embedding_map = embedding_map

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embedding_map[text] for text in texts]


class _TimeoutApiClient:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        del texts
        raise ApiTimeoutError("request timed out")


def _workspace_tmp_dir() -> Path:
    base = Path("pytest_tmp_manual") / "step14_langchain_retriever" / uuid4().hex
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
            "meta_extra": {"source": "unit-test", "rank": 1},
        },
    )


def _build_langchain_retriever(tmp_path: Path) -> LangChainRetriever:
    embeddings = {
        "doc-a": [1.0, 0.0, 0.0],
        "doc-b": [0.8, 0.2, 0.0],
        "doc-c": [0.0, 0.0, 1.0],
        "query-hsil": [1.0, 0.0, 0.0],
    }

    return LangChainRetriever(
        api_client=_FakeApiClient(embeddings),
        collection_name=f"step14_lc_{uuid4().hex}",
        persist_dir=tmp_path / "chroma",
    )


def test_langchain_retriever_returns_ranked_similar_cases_with_contract_fields() -> None:
    retriever = _build_langchain_retriever(_workspace_tmp_dir())
    docs = [
        _build_doc("CASE-A", "HSIL", "doc-a"),
        _build_doc("CASE-B", "HSIL", "doc-b"),
        _build_doc("CASE-C", "LSIL", "doc-c"),
    ]
    retriever.index_documents(docs)

    results = retriever.retrieve("query-hsil", top_k=2)

    assert len(results) == 2
    assert [item["case_id"] for item in results] == ["CASE-A", "CASE-B"]
    assert results[0]["similarity"] >= results[1]["similarity"]

    first = results[0]
    assert first["label"] == "HSIL"
    assert isinstance(first["similarity"], float)
    assert first["evidence"] == "doc-a"

    metadata = first["metadata"]
    assert metadata["case_id"] == "CASE-A"
    assert metadata["label"] == "HSIL"
    assert metadata["report_pdf_path"] == "data/HSIL/CASE-A/CASE-A.pdf"
    assert metadata["stain_text_path"] == "data/HSIL/CASE-A/stain.txt"
    assert metadata["image_paths"] == [
        "data/HSIL/CASE-A/1.jpg",
        "data/HSIL/CASE-A/2.jpg",
    ]
    assert metadata["meta_extra"] == {"source": "unit-test", "rank": 1}


def test_langchain_retriever_input_validation() -> None:
    retriever = _build_langchain_retriever(_workspace_tmp_dir())
    with pytest.raises(RetrieverError):
        retriever.index_documents([])
    with pytest.raises(RetrieverError):
        retriever.retrieve("", top_k=3)
    with pytest.raises(RetrieverError):
        retriever.retrieve("query-hsil", top_k=0)


def test_langchain_retriever_propagates_api_timeout_error() -> None:
    retriever = LangChainRetriever(
        api_client=_TimeoutApiClient(),
        collection_name=f"step14_lc_timeout_{uuid4().hex}",
        persist_dir=_workspace_tmp_dir() / "chroma",
    )

    with pytest.raises(ApiTimeoutError):
        retriever.retrieve("query-hsil", top_k=2)


def test_default_retriever_factory_switches_to_langchain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.infra.api_client.load_dotenv_if_present", lambda *args, **kwargs: None)
    monkeypatch.setenv("EMBEDDING_API_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(_workspace_tmp_dir() / "chroma_default"))

    retriever = build_default_vector_only_retriever(
        collection_name=f"step14_default_{uuid4().hex}",
    )

    assert isinstance(retriever, LangChainRetriever)
