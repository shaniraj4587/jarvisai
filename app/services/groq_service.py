"""
OLLAMA SERVICE MODULE
====================

This module handles general chat: no web search, only the Ollama LLM plus context
from the vector store (learning data + past chats). Used by ChatService for
POST /chat.

Uses a single Ollama model (gemma4:e4b) running locally.

FLOW:

1. get_response(question, chat_history) is called.
2. We ask the vector store for the top-k chunks most similar to the question (retrieval).
3. We build a system message: JARVIS_SYSTEM_PROMPT + current time + retrieved context.
4. We send to Ollama LLM.
5. We return the assistant's reply.

Context is only what we retrieve (no full dump of learning data), so token usage stays bounded.
"""

from typing import List, Optional

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

import logging

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, JARVIS_SYSTEM_PROMPT
from app.services.vector_store import VectorStoreService
from app.utils.time_info import get_time_information

logger = logging.getLogger("J.A.R.V.I.S")


# ============================================================================
# HELPER: ESCAPE CURLY BRACES FOR LANGCHAIN
# ============================================================================
# ============================================================================
# HELPER: ESCAPE CURLY BRACES FOR LANGCHAIN
# ============================================================================
# LangChain prompt templates use {variable_name}. If learning data or chat
# content contains { or }, the template engine can break. Doubling them
# makes them literal in the final string.


def escape_curly_braces(text: str) -> str:
    """
    Double every { and } so LangChain does not treat them as template variables.
    Learning data or chat content might contain { or }; without escaping, invoke() can fail.
    """

    if not text:
        return text

    return text.replace("{", "{{").replace("}", "}}")


# ============================================================================
# OLLAMA SERVICE CLASS
# ============================================================================


class GroqService:
    """
    General chat: retrieves context from the vector store and calls the Ollama LLM.
    Uses a single Ollama model (gemma4:e4b) running locally.
    """

    def __init__(self, vector_store_service: VectorStoreService):
        """
        Create one Ollama LLM client and store the vector store for retrieval.
        Ollama should be running locally at OLLAMA_BASE_URL (default: http://localhost:11434).
        """

        # Single Ollama LLM instance
        self.llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.8,
        )

        self.vector_store_service = vector_store_service

        logger.info(f"Initialized GroqService with Ollama model: {OLLAMA_MODEL}")
        logger.info(f"Ollama base URL: {OLLAMA_BASE_URL}")

    def get_response(
        self, question: str, chat_history: Optional[List[tuple]] = None
    ) -> str:
        """
        Return the assistant's reply for this question (general chat, no web search).
        Retrieves context from the vector store, builds the prompt, then calls Ollama LLM.
        """

        try:
            # Get relevant chunks from learning data and past chats (bounded token usage).
            # If retrieval fails (e.g. vector store not ready), use empty context so the LLM still answers.
            context = ""

            try:
                retriever = self.vector_store_service.get_retriever(k=10)

                context_docs = retriever.invoke(question)

                context = (
                    "\n".join([doc.page_content for doc in context_docs])
                    if context_docs
                    else ""
                )

            except Exception as retrieval_err:
                logger.warning(
                    "Vector store retrieval failed, using empty context: %s",
                    retrieval_err,
                )

            # Build system message: personality + current time + retrieved context.
            time_info = get_time_information()

            system_message = (
                JARVIS_SYSTEM_PROMPT + f"\n\nCurrent time and date: {time_info}"
            )

            if context:
                system_message += (
                    "\n\nRelevant context from your learning data "
                    f"and past conversations:\n{escape_curly_braces(context)}"
                )

            # Prompt template: system message, chat history placeholder, current question.
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_message),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", "{question}"),
                ]
            )

            # Convert (user, assistant) pairs to LangChain message objects.
            messages = []

            if chat_history:
                for human_msg, ai_msg in chat_history:
                    messages.append(HumanMessage(content=human_msg))

                    messages.append(AIMessage(content=ai_msg))

            # Build chain with Ollama LLM and invoke
            chain = prompt | self.llm

            response = chain.invoke({"history": messages, "question": question})

            return response

        except Exception as e:
            raise Exception(f"Error getting response from Ollama: {str(e)}") from e
