from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd
from PIL import Image
import base64
from langchain_core.messages import HumanMessage,SystemMessage
import mimetypes
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
import dotenv
import os
# Force HuggingFace to avoid using symlinks if possible
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END, MessagesState
import requests
import json
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
dotenv.load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature = 0)

class UniversalLoader:
    def __init__(self,llm):
        self.llm = llm

    def process_file(self, file_path: str):
        """
        Traffic Controller: Routes files to the correct reader.
        """
        # 1. Get extension and mime type
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # 2. DEFINE CODE EXTENSIONS (Treat these as text)
        code_extensions = {'.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.h', '.sql', '.md', '.json', '.xml', '.yaml', '.yml', '.txt'}

        if ext in code_extensions:
            return self._process_code(file_path, ext)
        
        elif mime_type and "pdf" in mime_type:
            return self._process_pdf(file_path)
        
        elif mime_type and "csv" in mime_type:
            return self._process_csv(file_path)
        
        elif mime_type and "image" in mime_type:
            return self._process_image(file_path)
        
        else:
            return f"Unsupported file type: {mime_type or ext}"
        
    def _process_code(self, file_path, ext):
        """Reads code files and wraps them in markdown."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Wrap in markdown so LLM knows it's code
            lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.html': 'html', '.sql': 'sql', '.css': 'css'}
            language = lang_map.get(ext, '')
            return f"```{language}\n{content}\n```"
        except Exception as e:
            return f"Error reading code file: {e}"
        
    def _process_txt(self,file_path):
        with open(file_path,'r') as f:
            return f.read()
        
    def _process_pdf(self,file_path):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        result = ""
        for page in pages:
            result += page.page_content + "\n"
        return result
    
    def _process_csv(self,file_path):
        df = pd.read_csv(file_path)
        return df.to_markdown(index=False)
    
    def _process_image(self,file_path):
        try:
            with open(file_path, 'rb') as f:
                    
                image_data = base64.b64encode(f.read()).decode('utf-8')
                
                Prompt = HumanMessage(content = [
                    {"type":"text","text":"Describe the following image in detail."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                ])
                response = self.llm.invoke([Prompt])
                return response.content

        except Exception as e:
            return "error processing image: " + str(e)
        

universalloader = UniversalLoader(model)
    
#embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
vector_store = FAISS.from_texts(["Nexus Initialized"], embeddings)

def index_files(file_paths):
    """
    Reads files -> Chunks them -> Saves to Vector DB (Locally)
    """
    all_documents = []
    
    for path in file_paths:
        print(f"Loading: {path}...")
        
        # Extract Text using your UniversalLoader
        raw_content = universalloader.process_file(path)
        
        # Convert to Document
        doc = Document(page_content=raw_content, metadata={"source": path})
        all_documents.append(doc)
        
    # Split into chunks
    splits = text_splitter.split_documents(all_documents)
    
    # Add to Vector Store
    if splits:
        vector_store.add_documents(splits)
        print(f"Successfully indexed {len(splits)} chunks locally!")
    else:
        print("No content found to index.")

search_tool = DuckDuckGoSearchRun()
search_tool.name = "search_tool"
search_tool.description = "web search tool to find more information about a topic"

retriever = vector_store.as_retriever(search_kwargs={"k": 2})

@tool
def retrieve_documents(query: str) -> str:
    """
    Search and retrieve information from internal documents, code, and policies.
    Use this tool when the user asks about specific files or internal knowledge.
    """
    pages = retriever.invoke(query)
    result = ""
    for page in pages:
        result += page.page_content + "\n\n"
    return result

python_repl = PythonREPL()
@tool
def python_interpreter(code: str) -> str:
    """
    A Python shell. Use this to execute python commands.
    Input should be a valid python script.
    Use this for math, data analysis, or processing text.
    ALWAYS print(...) your final result so I can see it.
    """
    try:
        result = python_repl.run(code)
        return f"Executed:\n{result}"
    except Exception as e:
        return f"Error: {e}" 

def should_continue(state: MessagesState) -> str:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM asks for a tool, go to "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, stop
    return END

# 1. The Approved Tools
tools = [search_tool, retrieve_documents, python_interpreter]

# 2. Bind Tools to Model
model = model.bind_tools(tools)
tool_node = ToolNode(tools)

# 3. Define the Agent Logic
def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# 4. Build the Graph
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

print("Prototype Complete. Ready to migrate to Backend.")

def get_nexus_response(user_prompt: str, files: list = None):
    """
    This function handles the AI logic.
    Currently, it processes text. Later, we will add RAG (File) support here.
    """
    
    try:
        if files and len(files)>0:
            index_files(files)
            file_names = ", ".join([os.path.basename(f) for f in files])
            user_prompt = f"System Note: The user just uploaded these files: {file_names}. \n\nUser Question: {user_prompt}"
        else:
            user_prompt = f"User Question: {user_prompt}"

        system_instruction = SystemMessage(content="""
        You are Nexus, an advanced AI with file-reading capabilities.
        
        CRITICAL RULES:
        1. You have a tool named 'retrieve_documents'.
        2. IF the user asks about "the file", "uploaded documents", or content you don't know:
           YOU MUST USE 'retrieve_documents' to look it up.
        3. DO NOT say "I cannot access files". You HAVE the tool. Use it.
        4. If the tool returns text, assume it is the correct content of the file.
        """)

        config = {"configurable": {"thread_id": "1"}}
        inputs = {"messages": [system_instruction,HumanMessage(content=user_prompt)]}
        result_state = app.invoke(inputs,config=config)
        last_message = result_state['messages'][-1]
        content = last_message.content
       
        if isinstance(content, list):
            text_parts = []
            for part in content:
                # Extract 'text' if it exists, otherwise convert whole part to string
                if isinstance(part, dict):
                    text_parts.append(part.get('text', str(part)))
                else:
                    text_parts.append(str(part))
            return "\n".join(text_parts)
        
        # Case B: Content is already a string
        if isinstance(content, str):
            return content
            
        # Case C: Fallback
        return str(content)
        
    except Exception as e:
        return f"I encountered an error processing your request: {str(e)}"