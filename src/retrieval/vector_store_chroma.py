from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import chromadb

from src.infra.api_client import load_dotenv_if_present
from src.retrieval.document_builder import RetrievalDocument


class VectorStoreError(ValueError):
    """Raised when Chroma vector store operations fail."""


class ChromaVectorStore:
    def __init__(
        self,
        *,
        collection_name: str = "case_records",
        persist_dir: str | Path | None = None,
    ) -> None:
        if not isinstance(collection_name, str) or not collection_name.strip():
            raise VectorStoreError("collection_name must be a non-empty string.")

        load_dotenv_if_present()
        raw_persist_dir = (
            str(persist_dir)
            if persist_dir is not None
            else os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        )
        if not isinstance(raw_persist_dir, str) or not raw_persist_dir.strip():
            raise VectorStoreError("persist_dir must be a non-empty string.")

        self.collection_name = collection_name
        self.persist_dir = Path(raw_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError("failed to initialize chroma vector store.") from exc

    def upsert_documents(
        self,
        documents: list[RetrievalDocument],
        embeddings: list[list[float]],
    ) -> None:
        if len(documents) == 0:
            raise VectorStoreError("documents must be a non-empty list.")
        if len(documents) != len(embeddings):
            raise VectorStoreError("documents and embeddings must have the same length.")

        ids: list[str] = []
        contents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        normalized_embeddings: list[list[float]] = []

        for idx, document in enumerate(documents):
            if not isinstance(document, RetrievalDocument):
                raise VectorStoreError(f"documents[{idx}] must be a RetrievalDocument.")

            ids.append(document.doc_id)
            contents.append(document.content)
            metadatas.append(dict(document.metadata))
            normalized_embeddings.append(self._normalize_vector(embeddings[idx], f"embeddings[{idx}]"))

        try:
            self._collection.upsert(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
                embeddings=normalized_embeddings,
            )
        except Exception as exc:
            raise VectorStoreError("failed to upsert documents into chroma.") from exc

    def query(self, *, query_embedding: list[float], top_k: int) -> list[dict[str, object]]:
        if not isinstance(query_embedding, list) or len(query_embedding) == 0:
            raise VectorStoreError("query_embedding must be a non-empty list.")
        if not isinstance(top_k, int) or top_k <= 0:
            raise VectorStoreError("top_k must be a positive integer.")

        normalized_query = self._normalize_vector(query_embedding, "query_embedding")

        try:
            raw = self._collection.query(
                query_embeddings=[normalized_query],
                n_results=top_k,
                include=["metadatas", "documents", "distances"],
            )
        except Exception as exc:
            raise VectorStoreError("failed to query chroma collection.") from exc

        documents = self._first_list(raw.get("documents"))
        metadatas = self._first_list(raw.get("metadatas"))
        distances = self._first_list(raw.get("distances"))
        ids = self._first_list(raw.get("ids"))

        results: list[dict[str, object]] = []
        for idx, document in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) and isinstance(metadatas[idx], dict) else {}
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            similarity = max(0.0, min(1.0, 1.0 - distance))
            doc_id = ids[idx] if idx < len(ids) else ""

            case_id = metadata.get("case_id", doc_id)
            label = metadata.get("label", "")

            results.append(
                {
                    "case_id": str(case_id),
                    "label": str(label),
                    "similarity": similarity,
                    "evidence": document if isinstance(document, str) else "",
                    "metadata": metadata,
                }
            )

        return results

    @staticmethod
    def _first_list(value: object) -> list[object]:
        if not isinstance(value, list) or len(value) == 0:
            return []
        first = value[0]
        return first if isinstance(first, list) else []

    @staticmethod
    def _normalize_vector(vector: object, field_name: str) -> list[float]:
        if not isinstance(vector, list) or len(vector) == 0:
            raise VectorStoreError(f"{field_name} must be a non-empty list.")

        normalized: list[float] = []
        for idx, value in enumerate(vector):
            if not isinstance(value, (int, float)):
                raise VectorStoreError(f"{field_name}[{idx}] must be numeric.")
            normalized.append(float(value))
        return normalized
