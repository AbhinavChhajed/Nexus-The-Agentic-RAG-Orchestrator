from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# 1. Load Environment Variables (API Keys)
load_dotenv()

# 2. Initialize the Model (The Brain)
# We initialize it here so we don't reload it with every request
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

def get_nexus_response(user_prompt: str, files: list = None):
    """
    This function handles the AI logic.
    Currently, it processes text. Later, we will add RAG (File) support here.
    """
    try:
        # If we have files later, we will process them here
        # For now, we just ask the LLM directly
        
        response = llm.invoke(user_prompt)
        return response.content
        
    except Exception as e:
        return f"I encountered an error processing your request: {str(e)}"