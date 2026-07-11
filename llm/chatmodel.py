"""
LLM response layer — now powered by the OpenAI Agents SDK with pgvector retrieval.

Public interface:
    async def get_response(req: ChatRequest, chat_id: int, db: Session)
        -> tuple[LLMResponseFormat, list[SourceCitation]]
"""

from __future__ import annotations

import os
from sqlalchemy.orm import Session

from agents import Runner
from dotenv import load_dotenv

from agent.rag_agent import RAGContext, rag_agent
from models.pymodel import ChatRequest, LLMResponseFormat, SourceCitation
from retriver.retriver import similarityretriver

load_dotenv()


async def get_response(req: ChatRequest, chat_id: int, db: Session):
    """
    Run the RAG agent for a user question and return a structured response
    together with source citations pulled from the pgvector document store.

    Args:
        req:      ChatRequest containing question + chat_history
        chat_id:  The chat ID to scope retrieval to
        db:       Active SQLAlchemy session

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
    rag_ctx = RAGContext(chat_id=chat_id, db=db)

    # ── 3. Run the agent ──────────────────────────────────────────────────────
    print("Starting OpenAI Agents SDK run...")
    result = await Runner.run(
        rag_agent,
        input=agent_input,
        context=rag_ctx,
    )

    llm_response: LLMResponseFormat = result.final_output
    print(f"Agent response: {llm_response}")

    # ── 4. Build source citations from pgvector via similarityretriver ────────
    source_chunks = await similarityretriver(question=req.question, chat_id=chat_id, k=4, db=db)

    sources: list[SourceCitation] = []
    seen: set[tuple[str, int]] = set()
    for chunk in source_chunks:
        meta = chunk.doc_metadata or {}
        filename = os.path.basename(meta.get("source", "unknown"))
        page = meta.get("page", 0) + 1  # convert 0-indexed → 1-indexed
        key = (filename, page)
        if key not in seen:
            seen.add(key)
            sources.append(SourceCitation(filename=filename, page=page))

    return llm_response, sources
