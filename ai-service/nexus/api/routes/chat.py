"""
POST /chat — main conversational endpoint.
"""

import os
import uuid

from fastapi import APIRouter

from nexus.config import get_settings
from nexus.api.schemas import ChatRequest, ChatResponse
from nexus.agent import get_nexus_response

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(data: ChatRequest):
    """Accept a user prompt and return the AI response."""
    settings = get_settings()
    thread_id = data.thread_id

    if not thread_id or thread_id == "new":
        thread_id = str(uuid.uuid4())

    # Gather any uploaded files
    files: list[str] = []
    if os.path.exists(settings.upload_dir):
        files = [
            os.path.join(settings.upload_dir, f)
            for f in os.listdir(settings.upload_dir)
            if os.path.isfile(os.path.join(settings.upload_dir, f))
        ]

    result = get_nexus_response(
        user_prompt=data.prompt,
        thread_id=thread_id,
        files=files,
    )

    return ChatResponse(response=result, thread_id=thread_id)
