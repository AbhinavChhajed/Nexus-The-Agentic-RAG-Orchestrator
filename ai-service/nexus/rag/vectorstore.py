"""
FAISS vector store singleton.

Initialises a FAISS index with a seed document and provides
accessor functions for the store and its retriever.
"""

from langchain_community.vectorstores import FAISS

from nexus.config import get_settings
from nexus.rag.embeddings import get_embeddings

# Module-level singleton — created on first import
_vector_store: FAISS | None = None


def get_vector_store() -> FAISS:
    """Return the global FAISS vector store, creating it on first call."""
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISS.from_texts(["Nexus Initialized"], get_embeddings())
    return _vector_store


def get_retriever():
    """Return a retriever backed by the global FAISS store."""
    settings = get_settings()
    return get_vector_store().as_retriever(
        search_kwargs={"k": settings.retriever_top_k}
    )
