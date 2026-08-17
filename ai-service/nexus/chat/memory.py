"""
LangGraph checkpointer backed by SQLite.

Manages the persistent SQLite connection and SqliteSaver instance
used by the LangGraph agent for conversation memory.
"""

import sqlite3
from functools import lru_cache

from langgraph.checkpoint.sqlite import SqliteSaver

from nexus.config import get_settings

# Module-level connection — kept alive for the lifetime of the process
_db_connection: sqlite3.Connection | None = None


def get_db_connection() -> sqlite3.Connection:
    """Return the shared SQLite connection for the memory database."""
    global _db_connection
    if _db_connection is None:
        settings = get_settings()
        _db_connection = sqlite3.connect(
            settings.memory_db_path, check_same_thread=False
        )
    return _db_connection


@lru_cache()
def get_checkpointer() -> SqliteSaver:
    """Return a configured SqliteSaver checkpointer (created once)."""
    conn = get_db_connection()
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()
    return checkpointer
