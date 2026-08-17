"""
POST /upload  — file upload
POST /rename  — rename a chat thread
"""

import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile

from nexus.config import get_settings
from nexus.api.schemas import RenameRequest
from nexus.chat.history import save_chat_title

router = APIRouter(tags=["files"])


@router.post("/upload")
async def upload(files: Optional[List[UploadFile]] = File(...)):
    """Save uploaded files to the upload directory."""
    settings = get_settings()

    if not files:
        return {"message": "No files received"}

    saved_filenames: list[str] = []

    for file in files:
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_filenames.append(file.filename)

    return {"message": "Files saved successfully", "filenames": saved_filenames}


@router.post("/rename")
async def rename_chat(data: RenameRequest):
    """Update the display title for a chat thread."""
    save_chat_title(data.thread_id, data.title)
    return {"message": "Title updated"}
