import os
import shutil
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Import your AI logic
from ai_logic import get_nexus_response

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize FastAPI
app = FastAPI(title="Nexus AI Backend")

# 3. Setup Upload Directory (Where files will be saved)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 4. ENABLE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body for Chat
class ChatRequest(BaseModel):
    prompt: str

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

@app.post("/chat")
async def chat_endpoint(data: ChatRequest):
    user_prompt = data.prompt
    
    files = []
    if os.path.exists(UPLOAD_DIR):
        files = [
            os.path.join(UPLOAD_DIR, f) 
            for f in os.listdir(UPLOAD_DIR) 
            if os.path.isfile(os.path.join(UPLOAD_DIR, f))
        ]
    
    result = get_nexus_response(user_prompt, files=files)
    
    return {"response": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)