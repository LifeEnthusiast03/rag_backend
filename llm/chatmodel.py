from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from models.pymodel import ChatRequest, LLMResponseFormat, SourceCitation
from retriver.fas import get_vector_store, chat_vector_store, save_chat_vector_store
from langchain_core.documents import Document
from uuid import uuid4
import asyncio
import os

load_dotenv()

# LLM is instantiated once at module level (not per request)
model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",   # stable, fast model instead of preview
)


async def get_response(req: ChatRequest, chatfileloc: str):
    # ── Load vector stores (served from in-memory cache after first call) ──────
    vector_store_doc = get_vector_store(chatfileloc)
    vector_store_chat = chat_vector_store(chatfileloc)

    retriever_doc  = vector_store_doc.as_retriever(search_kwargs={"k": 5})   # was 20
    retriever_chat = vector_store_chat.as_retriever(search_kwargs={"k": 5})  # was 20
    print("Successfully got retrievers")

    # ── Run retrieval + source search concurrently ────────────────────────────
    context_docs, context_chat, source_results = await asyncio.gather(
        retriever_doc.ainvoke(req.question),
        retriever_chat.ainvoke(req.question),
        asyncio.to_thread(
            vector_store_doc.similarity_search_with_score, req.question, k=4
        ),
    )

    # Format context strings
    context_str = "\n\n".join([doc.page_content for doc in context_docs])
    chat_history_str = (
        "\n".join([f"{msg.role}: {msg.content}" for msg in req.chat_history])
        if req.chat_history
        else "No previous chat history"
    )
    relevant_information = (
        "\n".join([doc.page_content for doc in context_chat])
        if context_chat
        else "No relevant past information"
    )

    # ── Build deduplicated source citations ───────────────────────────────────
    sources: list[SourceCitation] = []
    seen: set[tuple[str, int]] = set()
    for doc, _score in source_results:
        filename = os.path.basename(doc.metadata.get("source", "unknown"))
        page = doc.metadata.get("page", 0) + 1  # convert 0-indexed → 1-indexed
        key = (filename, page)
        if key not in seen:
            seen.add(key)
            sources.append(SourceCitation(filename=filename, page=page))

    # ── Pydantic output parser ─────────────────────────────────────────────────
    parser = PydanticOutputParser(pydantic_object=LLMResponseFormat)

    prompt = PromptTemplate(
        template=(
            "You are a very good teaching assistant. You give a concise and clear answer to questions.\n\n"
            "Question: {question}\n\n"
            "Context from knowledge base:\n{context}\n\n"
            "Previous chat history:\n{chathistory}\n\n"
            "Relevant information from past conversations:\n{relevant_information}\n\n"
            "Answer the question using the context and any related information from the chat history.\n"
            "Provide key points, assess your confidence, cite sources, and suggest follow-up questions.\n\n"
            "{format_instructions}"
        ),
        input_variables=["question", "context", "chathistory", "relevant_information"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    print("Starting API call to Gemini...")
    response: LLMResponseFormat = await chain.ainvoke({
        "question": req.question,
        "context": context_str,
        "chathistory": chat_history_str,
        "relevant_information": relevant_information,
    })
    print(response)
    # ── Persist Q&A pair to chat vector store and update cache ────────────────
    chat_doc = Document(
        page_content=(
            f"Q: {req.question}\n"
            f"A: {response.answer}\n"
            f"Key Points: {', '.join(response.key_points)}"
        ),
        metadata={
            "source": "AI",
            "question": req.question,
            "confidence": response.confidence_level,
        },
    )
    doc_uuid = str(uuid4())
    vector_store_chat.add_documents(documents=[chat_doc], ids=[doc_uuid])
    # Persist to disk AND keep cache in sync (avoids stale cache)
    save_chat_vector_store(chatfileloc, vector_store_chat)

    return response, sources
