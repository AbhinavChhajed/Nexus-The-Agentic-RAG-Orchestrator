"""
GET /history        — list all chat threads
GET /history/{id}   — get messages for a specific thread
"""

from fastapi import APIRouter

from nexus.chat.history import get_all_threads, get_chat_title, get_thread_history
from nexus.agent import get_compiled_graph

router = APIRouter(tags=["history"])


@router.get("/history")
async def list_threads():
    """Return all threads with their display titles, newest first."""
    threads = get_all_threads()
    history_list = []

    for tid in threads:
        saved_title = get_chat_title(tid)
        display_title = saved_title if saved_title else f"Chat {tid[:8]}"
        history_list.append({"id": tid, "title": display_title})

    return history_list[::-1]


@router.get("/history/{thread_id}")
async def get_chat_session(thread_id: str):
    """Return the messages for a specific thread."""
    graph = get_compiled_graph()
    messages = get_thread_history(thread_id, graph)
    return {"messages": messages}
