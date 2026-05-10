"""
J.A.R.V.I.S MAIN API
====================

Main FastAPI application for the J.A.R.V.I.S backend.

Features:
- General AI chat
- Realtime AI chat with Tavily search
- Persistent chat sessions
- FAISS vector memory retrieval
- Health monitoring
- Automatic startup/shutdown lifecycle handling

Run:
    python -m app.main

API Docs:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS

from app.models import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.groq_service import GroqService
from app.services.realtime_service import RealtimeGroqService
from app.services.vector_store import VectorStoreService
from config import VECTOR_STORE_DIR


# ============================================================================
# RATE LIMIT HANDLING
# ============================================================================

RATE_LIMIT_MESSAGE = (
    "You've reached your daily API limit for this assistant. "
    "Your credits will reset in a few hours, or you can upgrade your plan. "
    "Please try again later."
)


def _is_rate_limit_error(exc: Exception) -> bool:
    """
    Detect whether an exception is a Groq rate-limit error.
    """
    msg = str(exc).lower()

    return (
        "429" in str(exc)
        or "rate limit" in msg
        or "tokens per day" in msg
    )


# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("J.A.R.V.I.S")


# ============================================================================
# GLOBAL SERVICE REFERENCES
# ============================================================================

vector_store_service: VectorStoreService = None
groq_service: GroqService = None
realtime_service: RealtimeGroqService = None
chat_service: ChatService = None


# ============================================================================
# ASCII BANNER
# ============================================================================

def print_title():
    """
    Print startup banner.
    """

    title = r"""

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          J.A.R.V.I.S                                       ║
║                                                            ║
║        Just A Rather Very Intelligent System               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

"""

    print(title)


# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager.

    Handles:
    - Startup initialization
    - Service creation
    - Shutdown cleanup
    - Session persistence
    """

    global vector_store_service, groq_service, realtime_service, chat_service

    print_title()

    logger.info("=" * 60)
    logger.info("J.A.R.V.I.S - Starting Up...")
    logger.info("=" * 60)

    try:
        # ------------------------------------------------------------------
        # VECTOR STORE
        # ------------------------------------------------------------------

        logger.info("Initializing vector store service...")

        vector_store_service = VectorStoreService()
        vector_store_service.create_vector_store()

        logger.info("Vector store initialized successfully")

        # ------------------------------------------------------------------
        # GENERAL GROQ SERVICE
        # ------------------------------------------------------------------

        logger.info("Initializing Groq service (general chat)...")

        groq_service = GroqService(vector_store_service)

        logger.info("Groq service initialized successfully")

        # ------------------------------------------------------------------
        # REALTIME GROQ SERVICE
        # ------------------------------------------------------------------

        logger.info("Initializing Realtime Groq service...")

        realtime_service = RealtimeGroqService(vector_store_service)

        logger.info("Realtime Groq service initialized successfully")

        # ------------------------------------------------------------------
        # CHAT SERVICE
        # ------------------------------------------------------------------

        logger.info("Initializing chat service...")

        chat_service = ChatService(
            groq_service,
            realtime_service,
        )

        logger.info("Chat service initialized successfully")

        # ------------------------------------------------------------------
        # STARTUP COMPLETE
        # ------------------------------------------------------------------

        logger.info("=" * 60)
        logger.info("Service Status:")
        logger.info(" - Vector Store: Ready")
        logger.info(" - Groq AI (General): Ready")
        logger.info(" - Groq AI (Realtime): Ready")
        logger.info(" - Chat Service: Ready")
        logger.info("=" * 60)

        logger.info("J.A.R.V.I.S is online and ready!")
        logger.info("API:  http://localhost:8000")
        logger.info("Docs: http://localhost:8000/docs")

        logger.info("=" * 60)

        yield

        # ------------------------------------------------------------------
        # SHUTDOWN
        # ------------------------------------------------------------------

        logger.info("\nShutting down J.A.R.V.I.S...")

        if chat_service:
            for session_id in list(chat_service.sessions.keys()):
                chat_service.save_chat_session(session_id)

        logger.info("All sessions saved. Goodbye!")

    except Exception as e:
        logger.error(
            f"Fatal startup error: {e}",
            exc_info=True,
        )
        raise


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="J.A.R.V.I.S API",
    description="Just A Rather Very Intelligent System",
    lifespan=lifespan,
)


# ============================================================================
# CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """
    API discovery endpoint.
    """

    return {
        "message": "J.A.R.V.I.S API",
        "endpoints": {
            "/chat": "General chat",
            "/chat/realtime": "Realtime chat with Tavily search",
            "/chat/history/{session_id}": "Get chat history",
            "/health": "System health check",
        },
    }


# ============================================================================
# HEALTH ENDPOINT
# ============================================================================

@app.get("/health")
async def health():
    """
    Return system health information.
    """

    return {
        "status": "healthy",
        "vector_store": vector_store_service is not None,
        "groq_service": groq_service is not None,
        "realtime_service": realtime_service is not None,
        "chat_service": chat_service is not None,
    }


# ============================================================================
# GENERAL CHAT ENDPOINT
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    General chat endpoint (no web search).
    """

    if not chat_service:
        raise HTTPException(
            status_code=503,
            detail="Chat service not initialized",
        )

    try:
        # Create or load session
        session_id = chat_service.get_or_create_session(
            request.session_id
        )

        # Process general chat
        response_text = chat_service.process_message(
            session_id,
            request.message,
        )

        # Persist session
        chat_service.save_chat_session(session_id)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
        )

    except ValueError as e:
        logger.warning(f"Invalid session_id: {e}")

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        if _is_rate_limit_error(e):
            logger.warning(f"Rate limit hit: {e}")

            raise HTTPException(
                status_code=429,
                detail=RATE_LIMIT_MESSAGE,
            )

        logger.error(
            f"Error processing chat: {e}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}",
        )


# ============================================================================
# REALTIME CHAT ENDPOINT
# ============================================================================

@app.post("/chat/realtime", response_model=ChatResponse)
async def chat_realtime(request: ChatRequest):
    """
    Realtime chat endpoint with Tavily search.
    """

    if not chat_service:
        raise HTTPException(
            status_code=503,
            detail="Chat service not initialized",
        )

    if not realtime_service:
        raise HTTPException(
            status_code=503,
            detail="Realtime service not initialized",
        )

    try:
        session_id = chat_service.get_or_create_session(
            request.session_id
        )

        response_text = chat_service.process_realtime_message(
            session_id,
            request.message,
        )

        chat_service.save_chat_session(session_id)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
        )

    except ValueError as e:
        logger.warning(f"Invalid session_id: {e}")

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        if _is_rate_limit_error(e):
            logger.warning(f"Rate limit hit: {e}")

            raise HTTPException(
                status_code=429,
                detail=RATE_LIMIT_MESSAGE,
            )

        logger.error(
            f"Realtime chat error: {e}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}",
        )


# ============================================================================
# CHAT HISTORY ENDPOINT
# ============================================================================

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Return all chat messages for a session.
    """

    if not chat_service:
        raise HTTPException(
            status_code=503,
            detail="Chat service not initialized",
        )

    try:
        messages = chat_service.get_chat_history(session_id)

        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                }
                for msg in messages
            ],
        }

    except Exception as e:
        logger.error(
            f"Error retrieving history: {e}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}",
        )


# ============================================================================
# STANDALONE RUN
# ============================================================================

def run():
    """
    Start uvicorn server.
    """

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run()