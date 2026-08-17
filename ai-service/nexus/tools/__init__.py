from nexus.tools.search import search_tool
from nexus.tools.retriever import retrieve_documents
from nexus.tools.python_repl import python_interpreter


def get_all_tools() -> list:
    """Return the complete list of tools available to the agent."""
    return [search_tool, retrieve_documents, python_interpreter]


__all__ = ["search_tool", "retrieve_documents", "python_interpreter", "get_all_tools"]
