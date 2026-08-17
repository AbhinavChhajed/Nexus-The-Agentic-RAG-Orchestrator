"""
Embedding model initialisation.

Provides a factory that returns the configured embedding model instance.
Currently uses FastEmbed (BAAI/bge-small-en-v1.5) for local, fast embeddings.
"""

from functools import lru_cache

from langchain_community.embeddings import FastEmbedEmbeddings

from nexus.config import get_settings


@lru_cache()
def get_embeddings() -> FastEmbedEmbeddings:
    """Return a cached embedding model instance."""
    settings = get_settings()
    return FastEmbedEmbeddings(model_name=settings.embedding_model_name)
