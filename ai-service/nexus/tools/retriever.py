"""
RAG retriever tool — searches the FAISS vector store for relevant documents.
"""

from langchain_core.tools import tool

from nexus.rag.vectorstore import get_retriever


@tool
def retrieve_documents(query: str) -> str:
    """
    Search and retrieve information from internal documents, code, and policies.
    Use this tool when the user asks about specific files or internal knowledge.
    """
    retriever = get_retriever()
    pages = retriever.invoke(query)
    return "\n\n".join(page.page_content for page in pages)
