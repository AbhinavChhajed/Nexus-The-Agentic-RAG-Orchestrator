"""
File indexing pipeline.

Reads files through the UniversalLoader, chunks the content,
and inserts the chunks into the FAISS vector store.
"""

import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from nexus.config import get_settings
from nexus.rag.loaders import UniversalLoader
from nexus.rag.vectorstore import get_vector_store

logger = logging.getLogger(__name__)


def _get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Build a text splitter from current settings."""
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def index_files(file_paths: list[str], loader: UniversalLoader) -> int:
    """
    Read files → chunk → insert into the vector store.

    Returns the number of chunks indexed.
    """
    all_documents: list[Document] = []

    for path in file_paths:
        logger.info("Loading: %s ...", path)
        raw_content = loader.process_file(path)
        doc = Document(page_content=raw_content, metadata={"source": path})
        all_documents.append(doc)

    splitter = _get_text_splitter()
    splits = splitter.split_documents(all_documents)

    if splits:
        get_vector_store().add_documents(splits)
        logger.info("Successfully indexed %d chunks.", len(splits))
    else:
        logger.warning("No content found to index.")

    return len(splits)
