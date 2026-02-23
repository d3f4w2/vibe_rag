"""Retrieval-layer components for document preparation and query orchestration."""

from .document_builder import (
    DocumentBuildError,
    RetrievalDocument,
    build_retrieval_document,
    build_retrieval_documents,
)
from .langchain_retriever import LangChainRetriever
from .retriever import RetrieverError, VectorOnlyRetriever, build_default_vector_only_retriever
from .vector_store_chroma import ChromaVectorStore, VectorStoreError

__all__ = [
    "DocumentBuildError",
    "RetrievalDocument",
    "build_retrieval_document",
    "build_retrieval_documents",
    "LangChainRetriever",
    "RetrieverError",
    "VectorOnlyRetriever",
    "build_default_vector_only_retriever",
    "ChromaVectorStore",
    "VectorStoreError",
]
