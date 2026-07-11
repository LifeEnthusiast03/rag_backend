"""
RAG Agent using OpenAI Agents SDK.

Tools:
  - search_knowledge_base : searches the document chunks in pgvector (DocumentChunk table)
  - search_chat_history   : fetches recent assistant messages from the Message table
  - generate_citation     : formats a proper citation for content from uploaded docs
  - WebSearchTool         : built-in SDK web-search hosted tool

The agent is instantiated once at module level and re-used per request
with a per-request RunContextWrapper that carries `chat_id` and a DB session.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

from agents import Agent, RunContextWrapper, WebSearchTool, function_tool
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import select

from db.data_models import Message
from models.pymodel import LLMResponseFormat
from retriver.retriver import similarityretriver

load_dotenv()


# ── Per-request context ───────────────────────────────────────────────────────

@dataclass
class RAGContext:
    """Holds per-request state that tools need (which chat to query)."""
    chat_id: int
    db: Session


# ── Function Tools ────────────────────────────────────────────────────────────

@function_tool
async def search_knowledge_base(ctx: RunContextWrapper[RAGContext], query: str) -> str:
    """
    Search the uploaded document knowledge base for information relevant to the
    given query. Returns the top matching text chunks with their source metadata.
    Always call this tool FIRST for every user question.

    Args:
        query: The search query to look up in the knowledge base.
    """
    chat_id = ctx.context.chat_id
    db = ctx.context.db

    # Use similarityretriver — NOTE: this does NOT close db since we pass the
    # shared session; db.close() in retriver.py only runs when called standalone.
    results = await similarityretriver(question=query, chat_id=chat_id, k=5, db=db)

    if not results:
        return "No relevant documents found in the knowledge base."

    chunks = []
    for i, doc in enumerate(results):
        source = os.path.basename(doc.doc_metadata.get("source", "unknown")) if doc.doc_metadata else "unknown"
        page = (doc.doc_metadata.get("page", 0) + 1) if doc.doc_metadata else 1
        chunks.append(
            f"[Chunk {i+1} | Source: {source}, Page: {page}]\n"
            f"{doc.content}"
        )
    return "\n\n".join(chunks)


@function_tool
def search_chat_history(ctx: RunContextWrapper[RAGContext], query: str) -> str:
    """
    Search the conversation history for past Q&A pairs relevant to the current
    query. Use this to maintain context and avoid repeating explanations.
    Always call this AFTER searching the knowledge base.

    Args:
        query: The search query to look up in previous conversations.
    """
    chat_id = ctx.context.chat_id
    db = ctx.context.db

    # Fetch the last 10 messages (user + assistant) for context
    messages = db.scalars(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.message_id.desc())
        .limit(10)
    ).all()

    if not messages:
        return "No relevant information found in past conversations."

    # Reverse to chronological order
    messages = list(reversed(messages))
    chunks = [
        f"[{msg.role.capitalize()}]: {msg.content}"
        for msg in messages
    ]
    return "\n\n".join(chunks)


@function_tool
def generate_citation(
    filename: str,
    page: int,
    excerpt: str,
    topic: str,
) -> str:
    """
    Generate a formatted citation for a specific piece of content from the
    uploaded documents. Call this whenever you reference specific content
    from the knowledge base to make your answer verifiable and credible.

    Args:
        filename: The name of the source document file (e.g. "lecture_notes.pdf").
        page:     The page number where the content appears (1-indexed).
        excerpt:  A short verbatim or paraphrased excerpt from that page.
        topic:    A brief label describing what this citation supports
                  (e.g. "Definition of Photosynthesis").
    """
    year = datetime.now().year
    citation = (
        f"[{topic}] "
        f'"{excerpt}" '
        f"— {filename}, p. {page} "
        f"(Uploaded document, {year})"
    )
    return citation


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an expert teaching assistant that helps users understand and learn from \
the documents they have uploaded.

Your primary goal is to provide accurate, well-structured, and context-aware \
answers by combining information from multiple sources in the correct priority.

====================
SOURCE PRIORITY
====================

Always use sources in this order:

1. Uploaded documents (`search_knowledge_base`)
2. Previous conversation (`search_chat_history`)
3. Web search (only if necessary)

Never reverse this priority.

====================
TOOL USAGE
====================

For every user question:

Step 1:
Search the uploaded documents using `search_knowledge_base`.
Treat the uploaded documents as the primary and most authoritative source.
Never skip this step.

Step 2:
Search previous conversations using `search_chat_history`.
Use this to maintain context and avoid repeating explanations unnecessarily.

Step 3:
If important information is still missing or the user requests knowledge outside \
the uploaded material, use web search.
Never allow web results to override or contradict the uploaded documents unless \
the documents are clearly outdated or incomplete.
If there is a conflict between sources, explain it clearly.

Step 4:
Whenever you reference specific facts from the uploaded documents, call \
`generate_citation` to produce a proper citation for that content.
This makes your answer credible and verifiable.

====================
ANSWER QUALITY
====================

Every answer should:

• Be factually accurate.
• Stay grounded in the uploaded documents whenever possible.
• Preserve context from previous conversations.
• Avoid unsupported assumptions.
• Never invent facts.
• Prefer completeness over brevity while avoiding unnecessary repetition.

====================
EXPLANATION STYLE
====================

When explaining concepts:

- Begin with a concise direct answer.
- Explain the reasoning.
- Include important details.
- Use bullet points when appropriate.
- Use examples if they improve understanding.
- Simplify complex topics without losing accuracy.

For comparison questions:
- Compare items point by point.

For procedural questions:
- Explain each step in order.

For summaries:
- Capture the key ideas while preserving important details.

====================
WHEN INFORMATION IS MISSING
====================

If the uploaded documents do not fully answer the question:

- Answer using the available document information.
- Supplement only the missing parts using web search.
- Clearly distinguish document-based information from supplementary information.

If sufficient information cannot be found:

- Say so honestly.
- Do not hallucinate.

====================
RESPONSE STYLE
====================

Be professional, educational, concise, and easy to understand.

Do not mention internal tools, embeddings, retrieval, vector stores, or \
implementation details.

Do not state that you "searched the knowledge base" or "used a tool."

Present the answer naturally, as if you simply know the material.

====================
OUTPUT
====================

Return ONLY valid JSON that matches the required output schema.
No markdown fences.
No additional text outside the JSON object.
"""


# ── Agent definition ──────────────────────────────────────────────────────────

rag_agent: Agent[RAGContext] = Agent(
    name="RAG Teaching Assistant",
    instructions=SYSTEM_PROMPT,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    tools=[
        search_knowledge_base,
        search_chat_history,
        generate_citation,
        WebSearchTool(),
    ],
    output_type=LLMResponseFormat,
)
