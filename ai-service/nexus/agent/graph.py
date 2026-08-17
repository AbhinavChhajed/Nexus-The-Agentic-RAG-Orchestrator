"""
LangGraph agent graph — builds, compiles, and exposes the agentic workflow.

This module is the heart of Nexus. It:
1. Creates the LLM instance (Gemini 3.7 Flash)
2. Binds all tools to the model
3. Constructs the StateGraph (agent ↔ tools loop)
4. Compiles with the SQLite checkpointer for memory
5. Exposes get_nexus_response() as the main orchestrator
"""

import logging
import os
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from nexus.config import get_settings
from nexus.tools import get_all_tools
from nexus.chat.memory import get_checkpointer
from nexus.rag.loaders import UniversalLoader
from nexus.rag.indexer import index_files

logger = logging.getLogger(__name__)


# ── LLM ──────────────────────────────────────────────────────────────────


def _create_llm() -> ChatGoogleGenerativeAI:
    """Create the base LLM instance from settings."""
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
    )


# ── Graph Construction ───────────────────────────────────────────────────


@lru_cache()
def get_compiled_graph():
    """
    Build and compile the LangGraph agent.

    Returns the compiled graph (with checkpointer) — a singleton
    that is reused across all requests.
    """
    llm = _create_llm()
    tools = get_all_tools()

    # Bind tools to the model so it can emit tool calls
    model_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    # Define node functions (closure over model_with_tools)
    def call_model(state: MessagesState):
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> str:
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return "end"

    # Build the graph
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": "__end__"})
    workflow.add_edge("tools", "agent")

    # Compile with persistent memory
    checkpointer = get_checkpointer()
    return workflow.compile(checkpointer=checkpointer)


# ── Orchestrator ─────────────────────────────────────────────────────────


def get_nexus_response(
    user_prompt: str,
    thread_id: str,
    files: list[str] | None = None,
) -> str:
    """
    Main entry point for generating an AI response.

    Handles file indexing (if files are uploaded), injects the system
    prompt, invokes the agent graph, and returns the final text response.
    """
    settings = get_settings()
    graph = get_compiled_graph()

    try:
        # Index any uploaded files into the vector store
        if files:
            llm = _create_llm()
            loader = UniversalLoader(llm)
            index_files(files, loader)
            file_names = ", ".join(os.path.basename(f) for f in files)
            user_prompt = (
                f"System Note: The user just uploaded these files: {file_names}.\n\n"
                f"User Question: {user_prompt}"
            )
        else:
            user_prompt = f"User Question: {user_prompt}"

        system_instruction = SystemMessage(content=settings.system_prompt)
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [system_instruction, HumanMessage(content=user_prompt)]}

        result_state = graph.invoke(inputs, config=config)
        last_message = result_state["messages"][-1]
        content = last_message.content

        # Normalise multimodal / list content
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict):
                    text_parts.append(part.get("text", str(part)))
                else:
                    text_parts.append(str(part))
            return "\n".join(text_parts)

        if isinstance(content, str):
            return content

        return str(content)

    except Exception as e:
        logger.exception("Error in get_nexus_response")
        return f"I encountered an error processing your request: {e}"
