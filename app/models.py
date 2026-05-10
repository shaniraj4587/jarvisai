"""
DATA MODELS MODULE
==================

Pydantic models used across the J.A.R.V.I.S API.

These models provide:
- Request validation
- Response serialization
- Internal chat session structure
- Type safety across services
"""

from typing import List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# CHAT MESSAGE MODEL
# ============================================================================


class ChatMessage(BaseModel):
    """
    A single message inside a conversation.

    Example:
        {
            "role": "user",
            "content": "Hello Jarvis"
        }
    """

    role: str
    content: str


# ============================================================================
# CHAT REQUEST MODEL
# ============================================================================


class ChatRequest(BaseModel):
    """
    Request body for:
    - POST /chat
    - POST /chat/realtime

    Fields:
    - message:
        User message text.

    - session_id:
        Optional existing session ID.
        If omitted, a new session is created.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description="User message text",
    )

    session_id: Optional[str] = Field(
        default=None,
        description="Optional existing session ID",
    )


# ============================================================================
# CHAT RESPONSE MODEL
# ============================================================================


class ChatResponse(BaseModel):
    """
    Response returned by chat endpoints.

    Example:
        {
            "response": "Hello, how may I assist you?",
            "session_id": "uuid-here"
        }
    """

    response: str
    session_id: str


# ============================================================================
# CHAT HISTORY MODEL
# ============================================================================


class ChatHistory(BaseModel):
    """
    Internal representation of an entire conversation.

    Used for:
    - Saving sessions to disk
    - Loading sessions from disk
    - Passing structured chat history between services
    """

    session_id: str
    messages: List[ChatMessage]
