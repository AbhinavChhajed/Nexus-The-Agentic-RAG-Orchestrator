"""
Chat history and thread management.

Handles:
- Thread title CRUD (separate SQLite database)
- Listing all threads from the checkpoint database
- Retrieving human-readable message history for a thread
"""

import logging
import sqlite3

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from nexus.config import get_settings
from nexus.chat.memory import get_db_connection

logger = logging.getLogger(__name__)


# ── Title Database ───────────────────────────────────────────────────────


def _get_title_connection() -> sqlite3.Connection:
    """Return a connection to the title database."""
    settings = get_settings()
    return sqlite3.connect(settings.title_db_path, check_same_thread=False)


def init_title_db() -> None:
    """Create the chat_titles table if it doesn't exist."""
    with _get_title_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_titles (
                thread_id TEXT PRIMARY KEY,
                title TEXT
            )
        """)
        conn.commit()


def save_chat_title(thread_id: str, title: str) -> None:
    """Insert or update the display title for a thread."""
    with _get_title_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO chat_titles (thread_id, title) VALUES (?, ?)",
            (thread_id, title),
        )
        conn.commit()


def get_chat_title(thread_id: str) -> str | None:
    """Return the saved title for a thread, or None."""
    with _get_title_connection() as conn:
        cursor = conn.execute(
            "SELECT title FROM chat_titles WHERE thread_id = ?", (thread_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None


# ── Thread Listing ───────────────────────────────────────────────────────


def get_all_threads() -> list[str]:
    """Query all distinct thread IDs from the memory database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error("Error retrieving threads: %s", e)
        return []


# ── Message History ──────────────────────────────────────────────────────


def get_thread_history(thread_id: str, compiled_graph) -> list[dict]:
    """
    Fetch the human-readable message history for a thread.

    Filters out internal ToolMessages, SystemMessages,
    and empty AI tool-call requests.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state = compiled_graph.get_state(config)

    if not state.values:
        return []

    messages = state.values.get("messages", [])
    history: list[dict] = []

    for msg in messages:
        # Skip internal messages
        if isinstance(msg, (SystemMessage, ToolMessage)):
            continue

        # Skip empty content (tool-call-only AI messages)
        if not msg.content or not str(msg.content).strip():
            continue

        role = "user" if isinstance(msg, HumanMessage) else "Nexus"
        content = msg.content

        # Flatten list-type content (multimodal messages)
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict):
                    text_parts.append(part.get("text", ""))
                else:
                    text_parts.append(str(part))
            content = "\n".join(text_parts)

        history.append({"role": role, "content": content})

    return history
