import os
import shutil
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import uuid
from ai_logic import get_nexus_response,get_thread_history,get_all_threads,save_chat_title,get_chat_title
load_dotenv()

app = FastAPI(title="Nexus AI Backend")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    thread_id:str

class RenameRequest(BaseModel):
    thread_id: str
    title: str

@app.post("/rename")
async def rename_chat(data: RenameRequest):
    save_chat_title(data.thread_id, data.title)
    return {"message": "Title updated"}

@app.post("/upload")
async def upload(files: Optional[List[UploadFile]] = File(...)):
    if not files:
        return {"message": "No files received"}
    
    saved_filenames = []
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        saved_filenames.append(file.filename)
        
    return {"message": "Files saved successfully", "filenames": saved_filenames}

@app.get("/history")
async def get_history():
    threads = get_all_threads()
    history_list = []
    
    for tid in threads:
        saved_title = get_chat_title(tid)
        display_title = saved_title if saved_title else f"Chat {tid[:8]}"
        history_list.append({"id": tid, "title": display_title})
    
    return history_list[::-1]


@app.get("/history/{thread_id}")
async def get_chat_session(thread_id: str):
    """Returns the messages for a specific thread."""
    messages = get_thread_history(thread_id)
    return {"messages": messages}


@app.post("/chat")
async def chat_endpoint(data: ChatRequest):
    thread_id = data.thread_id
    if not thread_id or thread_id == 'new':
        thread_id = str(uuid.uuid4())


    user_prompt = data.prompt
    
    files = []
    if os.path.exists(UPLOAD_DIR):
        files = [
            os.path.join(UPLOAD_DIR, f) 
            for f in os.listdir(UPLOAD_DIR) 
            if os.path.isfile(os.path.join(UPLOAD_DIR, f))
        ]
    
    result = get_nexus_response(user_prompt=user_prompt, thread_id=thread_id, files=files)
    
    return {"response": result, "thread_id":thread_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)