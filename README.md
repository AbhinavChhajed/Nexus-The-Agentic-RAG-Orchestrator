# Nexus-The-Agentic-RAG-Orchestrator

```How to run application```

# setup vitual environment first:

python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies

pip install -r requirements.txt

# Configure API Keys    (code wont work without this step!!!)

this project uses google gemini api key
create a .env file inside ai-service folder
and enter you api key there

# note: 
embedding uses FastEmbedEmbeddings here also you can use google gemini embedding by removing comments in import and when declaring embedding

# run server (in terminal)

cd ai-service
uvicorn main:app --reload

# run application (in new terminal)

cd app
npm run dev

```About this app```

# Features

1. Chat ai-agent answers your question also contain memory element to keep chat flow consistent
2. RAG based question-answering possible
3. you can save chat and load old chats from chat history
4. rename you chat with double tapping on it in chat history sidebar
5. all chats are stored in a local database that will be created if already not exist
6. ai-agent can use multiple tools like:

# tool list

1. web search
2. python interpreter (can be used by ai like a calulator)
3. RAG tool

these tools increases ai agent's capabilities to next level

