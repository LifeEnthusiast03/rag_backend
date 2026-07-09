"""
LLM response layer — now powered by the OpenAI Agents SDK.

Public interface is unchanged:
    async def get_response(req: ChatRequest, chatfileloc: str)
        -> tuple[LLMResponseFormat, list[SourceCitation]]
"""

from __future__ import annotations

import asyncio
import os
from uuid import uuid4

from agents import Runner
from dotenv import load_dotenv
from langchain_core.documents import Document

from agent.rag_agent import RAGContext, rag_agent
from models.pymodel import ChatRequest, LLMResponseFormat, SourceCitation
from retriver.fas import (
    chat_vector_store,
    get_vector_store,
    save_chat_vector_store,
)

load_dotenv()


async def get_response(req: ChatRequest, chatfileloc: str):
    """
    Run the RAG agent for a user question and return a structured response
    together with source citations pulled from the document vector store.

    Args:
        req:          ChatRequest containing question + chat_history
        chatfileloc:  Path to the folder that holds the FAISS indexes

    Returns:
        (LLMResponseFormat, list[SourceCitation])
    """

    # ── 1. Build the input message for the agent ──────────────────────────────
    chat_history_str = (
        "\n".join([f"{msg.role}: {msg.content}" for msg in req.chat_history])
        if req.chat_history
        else "No previous chat history."
    )

    agent_input = (
        f"Chat history so far:\n{chat_history_str}\n\n"
        f"User question: {req.question}"
    )

    # ── 2. Create per-request context ─────────────────────────────────────────
    rag_ctx = RAGContext(chatfileloc=chatfileloc)

    # ── 3. Run the agent ──────────────────────────────────────────────────────
    print("Starting OpenAI Agents SDK run...")
    result = await Runner.run(
        rag_agent,
        input=agent_input,
        context=rag_ctx,
    )

    llm_response: LLMResponseFormat = result.final_output
    print(f"Agent response: {llm_response}")

    # ── 4. Build source citations from vector store ───────────────────────────
    # Run similarity search in a thread (FAISS is synchronous)
    vector_store_doc = get_vector_store(chatfileloc)
    source_results = await asyncio.to_thread(
        vector_store_doc.similarity_search_with_score, req.question, k=4
    )

    sources: list[SourceCitation] = []
    seen: set[tuple[str, int]] = set()
    for doc, _score in source_results:
        filename = os.path.basename(doc.metadata.get("source", "unknown"))
        page = doc.metadata.get("page", 0) + 1  # convert 0-indexed → 1-indexed
        key = (filename, page)
        if key not in seen:
            seen.add(key)
            sources.append(SourceCitation(filename=filename, page=page))

    # ── 5. Persist Q&A to chat vector store ───────────────────────────────────
    vector_store_chat = chat_vector_store(chatfileloc)
    chat_doc = Document(
        page_content=(
            f"Q: {req.question}\n"
            f"A: {llm_response.answer}\n"
            f"Key Points: {', '.join(llm_response.key_points)}"
        ),
        metadata={
            "source": "AI",
            "question": req.question,
            "confidence": llm_response.confidence_level,
        },
    )
    doc_uuid = str(uuid4())
    vector_store_chat.add_documents(documents=[chat_doc], ids=[doc_uuid])
    # Persist to disk AND keep cache in sync (avoids stale cache)
    save_chat_vector_store(chatfileloc, vector_store_chat)

    return llm_response, sources
