from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.infra.api_client import (
    ApiAuthError,
    ApiRateLimitError,
    ApiResponseError,
    ApiTimeoutError,
    load_dotenv_if_present,
)
from src.retrieval.document_builder import RetrievalDocument
from src.retrieval.metadata_codec import restore_metadata_from_chroma, sanitize_metadata_for_chroma
from src.retrieval.retriever import EmbeddingClientProtocol, RetrieverError


class ApiClientEmbeddingsAdapter(Embeddings):
    """LangChain embeddings adapter backed by the project's ApiClient contract."""

    def __init__(self, api_client: EmbeddingClientProtocol) -> None:
        self._api_client = api_client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._api_client.embed_texts(texts)
        return self._normalize_vectors(vectors, expected_len=len(texts), field_name="texts")

    def embed_query(self, text: str) -> list[float]:
        vectors = self._api_client.embed_texts([text])
        normalized = self._normalize_vectors(
            vectors,
            expected_len=1,
            field_name="query_text",
        )
        return normalized[0]

    @staticmethod
    def _normalize_vectors(
        vectors: object,
        *,
        expected_len: int,
        field_name: str,
    ) -> list[list[float]]:
        if not isinstance(vectors, list):
            raise RetrieverError(f"embedding client returned non-list for {field_name}.")
        if len(vectors) != expected_len:
            raise RetrieverError(
                f"embedding client returned {len(vectors)} vectors for {field_name}, "
                f"expected {expected_len}."
            )

        normalized: list[list[float]] = []
        for idx, vector in enumerate(vectors):
            if not isinstance(vector, list) or len(vector) == 0:
                raise RetrieverError(f"embedding vector[{idx}] for {field_name} must be non-empty.")
            normalized_vector: list[float] = []
            for dim, value in enumerate(vector):
                if not isinstance(value, (int, float)):
                    raise RetrieverError(
                        f"embedding vector[{idx}][{dim}] for {field_name} must be numeric."
                    )
                normalized_vector.append(float(value))
            normalized.append(normalized_vector)

        return normalized


class LangChainRetriever:
    """Retriever implementation migrated to LangChain + Chroma."""

    def __init__(
        self,
        *,
        api_client: EmbeddingClientProtocol,
        collection_name: str = "case_records",
        persist_dir: str | Path | None = None,
    ) -> None:
        if not isinstance(collection_name, str) or not collection_name.strip():
            raise RetrieverError("collection_name must be a non-empty string.")

        load_dotenv_if_present()
        raw_persist_dir = (
            str(persist_dir)
            if persist_dir is not None
            else os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        )
        if not isinstance(raw_persist_dir, str) or not raw_persist_dir.strip():
            raise RetrieverError("persist_dir must be a non-empty string.")

        self.collection_name = collection_name
        self.persist_dir = Path(raw_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._embeddings = ApiClientEmbeddingsAdapter(api_client)
        try:
            self._vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self._embeddings,
                persist_directory=str(self.persist_dir),
                collection_metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise RetrieverError("failed to initialize langchain chroma retriever.") from exc

    def index_documents(self, documents: list[RetrievalDocument]) -> None:
        if not isinstance(documents, list) or len(documents) == 0:
            raise RetrieverError("documents must be a non-empty list.")

        lc_documents: list[Document] = []
        ids: list[str] = []
        for idx, document in enumerate(documents):
            if not isinstance(document, RetrievalDocument):
                raise RetrieverError(f"documents[{idx}] must be a RetrievalDocument.")
            try:
                metadata = sanitize_metadata_for_chroma(
                    dict(document.metadata),
                    field_name=f"documents[{idx}].metadata",
                )
            except ValueError as exc:
                raise RetrieverError(str(exc)) from exc
            lc_documents.append(
                Document(
                    id=document.doc_id,
                    page_content=document.content,
                    metadata=metadata,
                )
            )
            ids.append(document.doc_id)

        try:
            self._vector_store.add_documents(lc_documents, ids=ids)
        except (ApiTimeoutError, ApiAuthError, ApiRateLimitError, ApiResponseError):
            raise
        except ValueError as exc:
            raise RetrieverError(str(exc)) from exc
        except Exception as exc:
            raise RetrieverError("failed to upsert documents into langchain chroma.") from exc

    def retrieve(self, query_text: str, *, top_k: int = 5) -> list[dict[str, object]]:
        if not isinstance(query_text, str) or not query_text.strip():
            raise RetrieverError("query_text must be a non-empty string.")
        if not isinstance(top_k, int) or top_k <= 0:
            raise RetrieverError("top_k must be a positive integer.")

        try:
            docs_with_scores = self._vector_store.similarity_search_with_relevance_scores(
                query_text,
                k=top_k,
            )
        except (ApiTimeoutError, ApiAuthError, ApiRateLimitError, ApiResponseError):
            raise
        except ValueError as exc:
            raise RetrieverError(str(exc)) from exc
        except Exception as exc:
            raise RetrieverError("failed to query langchain chroma retriever.") from exc

        similar_cases: list[dict[str, object]] = []
        for doc, score in docs_with_scores:
            metadata = (
                restore_metadata_from_chroma(doc.metadata)
                if isinstance(doc.metadata, dict)
                else {}
            )
            case_id = metadata.get("case_id") or doc.id or ""
            label = metadata.get("label", "")
            similarity = self._normalize_similarity(score)
            evidence = doc.page_content if isinstance(doc.page_content, str) else ""

            similar_cases.append(
                {
                    "case_id": str(case_id),
                    "label": str(label),
                    "similarity": similarity,
                    "evidence": evidence,
                    "metadata": metadata,
                }
            )

        similar_cases.sort(
            key=lambda item: float(item.get("similarity", 0.0)),
            reverse=True,
        )
        return similar_cases

    @staticmethod
    def _normalize_similarity(value: object) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))
