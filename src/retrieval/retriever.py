from __future__ import annotations

from typing import Protocol

from src.infra.api_client import ApiClient
from src.retrieval.document_builder import RetrievalDocument
from src.retrieval.vector_store_chroma import ChromaVectorStore


class RetrieverError(ValueError):
    """Raised when retrieval input validation or orchestration fails."""


class EmbeddingClientProtocol(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class VectorStoreProtocol(Protocol):
    def upsert_documents(
        self,
        documents: list[RetrievalDocument],
        embeddings: list[list[float]],
    ) -> None:
        ...

    def query(self, *, query_embedding: list[float], top_k: int) -> list[dict[str, object]]:
        ...


class VectorOnlyRetriever:
    def __init__(
        self,
        *,
        api_client: EmbeddingClientProtocol,
        vector_store: VectorStoreProtocol,
    ) -> None:
        self._api_client = api_client
        self._vector_store = vector_store

    def index_documents(self, documents: list[RetrievalDocument]) -> None:
        if not isinstance(documents, list) or len(documents) == 0:
            raise RetrieverError("documents must be a non-empty list.")

        texts = [document.content for document in documents]
        embeddings = self._api_client.embed_texts(texts)
        self._vector_store.upsert_documents(documents, embeddings)

    def retrieve(self, query_text: str, *, top_k: int = 5) -> list[dict[str, object]]:
        if not isinstance(query_text, str) or not query_text.strip():
            raise RetrieverError("query_text must be a non-empty string.")
        if not isinstance(top_k, int) or top_k <= 0:
            raise RetrieverError("top_k must be a positive integer.")

        query_embeddings = self._api_client.embed_texts([query_text])
        if len(query_embeddings) != 1:
            raise RetrieverError("embedding client must return exactly one query embedding.")
        return self._vector_store.query(query_embedding=query_embeddings[0], top_k=top_k)


def build_default_vector_only_retriever(
    *,
    collection_name: str = "case_records",
) -> VectorOnlyRetriever:
    return VectorOnlyRetriever(
        api_client=ApiClient(),
        vector_store=ChromaVectorStore(collection_name=collection_name),
    )
