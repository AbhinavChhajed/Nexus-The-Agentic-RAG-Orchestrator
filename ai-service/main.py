import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import FastAPI, File, UploadFile
from typing import List,Optional
from ai_logic import get_nexus_response

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize FastAPI
app = FastAPI(title="Nexus AI Backend")

# 3. ENABLE CORS (Critical for React Connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/upload")
async def upload(files: Optional[List[UploadFile]] = File(...)):
    return [file.filename for file in files]

@app.post("/chat")
async def chat_endpoint(data: dict):
    prompt = data.get("prompt", "")

    result = get_nexus_response(prompt)
    
   
    return {"response": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)