# J.A.R.V.I.S Backend API

A FastAPI-powered AI assistant backend with:

- General AI chat
- Real-time web search
- Persistent sessions
- Vector memory (FAISS)
- Local embeddings
- Tavily integration
- Groq LLM support

---

# Features

## General Chat (`/chat`)
- Pure LLM conversation
- Uses vector memory retrieval
- No internet access
- Fast responses

## Realtime Chat (`/chat/realtime`)
- Performs Tavily web search first
- Combines:
  - Search results
  - Vector memory
  - Chat history
- Sends all context to Groq AI

## Persistent Sessions
- Conversations survive restarts
- Stored as JSON files
- Shared between general and realtime chat modes

## Vector Memory
- FAISS vector database
- HuggingFace sentence-transformers embeddings
- Learns from:
  - `database/learning_data/*.txt`
  - `database/chats_data/*.json`

---

# Project Structure

```text
project/
│
├── app/
│   ├── main.py
│   ├── models.py
│   │
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── groq_service.py
│   │   ├── realtime_service.py
│   │   └── vector_store.py
│   │
│   └── utils/
│       ├── retry.py
│       └── time_info.py
│
├── database/
│   ├── chats_data/
│   ├── learning_data/
│   └── vector_store/
│
├── run.py
├── test.py
├── requirements.txt
├── .env
└── README.md
```

---

# Installation

## 1. Clone Repository

```bash
git clone <your-repository-url>
cd project
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
# ============================================================================
# USER / ASSISTANT SETTINGS
# ============================================================================

JARVIS_USER_TITLE=Aarav Malhotra
ASSISTANT_NAME=Alfred


# ============================================================================
# GROQ SETTINGS
# ============================================================================

GROQ_MODEL=llama-3.3-70b-versatile

GROQ_API_KEY=your_primary_groq_api_key
GROQ_API_KEY_2=your_secondary_groq_api_key
GROQ_API_KEY_3=your_backup_groq_api_key


# ============================================================================
# TAVILY SETTINGS
# ============================================================================

TAVILY_API_KEY=your_tavily_api_key
```

---

# Run the Server

Start the backend server:

```bash
python run.py
```

Server URL:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

# Test the API

Run:

```bash
python test.py
```

Example `test.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "message": "Hello Jarvis"
    }
)

print(response.json())
```

---

# API Endpoints

## Root Endpoint

```http
GET /
```

Returns API information and endpoint list.

---

## Health Check

```http
GET /health
```

Example Response:

```json
{
  "status": "healthy"
}
```

---

## General Chat

```http
POST /chat
```

Request:

```json
{
  "message": "What is Python?"
}
```

Response:

```json
{
  "response": "Python is a programming language...",
  "session_id": "uuid-here"
}
```

---

## Realtime Chat

```http
POST /chat/realtime
```

Request:

```json
{
  "message": "Latest AI news"
}
```

Response:

```json
{
  "response": "Based on recent search results...",
  "session_id": "uuid-here"
}
```

---

## Chat History

```http
GET /chat/history/{session_id}
```

Response:

```json
{
  "session_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hello! How may I assist you?"
    }
  ]
}
```

---

# How Vector Memory Works

1. Loads all `.txt` learning files
2. Loads saved chat sessions
3. Splits text into chunks
4. Creates embeddings locally
5. Stores vectors in FAISS
6. Retrieves relevant chunks during chat

---

# Learning Data

Add `.txt` files inside:

```text
database/learning_data/
```

Example:

```text
database/learning_data/python.txt
```

Restart the server after adding new files.

---

# Chat Storage

Chat sessions are stored in:

```text
database/chats_data/
```

Each conversation is saved as:

```text
<session_id>.json
```

---

# Technologies Used

- FastAPI
- LangChain
- FAISS
- HuggingFace Embeddings
- Groq API
- Tavily Search
- Uvicorn
- Pydantic

---

# Development

Run with auto-reload enabled:

```bash
python run.py
```

Any Python file changes automatically restart the server.

---

# Security Notes

- Never commit `.env`
- Rotate exposed API keys immediately
- Add `.env` to `.gitignore`

Example:

```gitignore
# Environment variables
.env

# Python cache
__pycache__/
*.pyc

# Virtual environments
venv/
.env/

# Vector database
database/vector_store/

# Chat sessions
database/chats_data/
```

---

# Production Deployment

Recommended options:

- Docker
- Gunicorn + Uvicorn workers
- Nginx reverse proxy

Disable `reload=True` in production.

---

# License

MIT License

---

# Author

## J.A.R.V.I.S
**Just A Rather Very Intelligent System**