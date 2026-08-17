"""
Pydantic request / response schemas for the API layer.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat message."""
    prompt: str
    thread_id: str


class ChatResponse(BaseModel):
    """Outgoing chat response."""
    response: str
    thread_id: str


class RenameRequest(BaseModel):
    """Rename a chat thread."""
    thread_id: str
    title: str


class ThreadSummary(BaseModel):
    """Summary of a thread for the history list."""
    id: str
    title: str
