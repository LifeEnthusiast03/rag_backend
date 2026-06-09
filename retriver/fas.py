from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4
from pathlib import Path
import os

# Embedding model is loaded ONCE at module level (heavy operation)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# ─── In-memory cache: avoids reloading FAISS from disk on every request ───────
_vector_store_cache: dict[str, FAISS] = {}

def _get_cached(cache_key: str, persist_path: Path) -> FAISS:
    """Return cached vector store, or load from disk and cache it."""
    if cache_key not in _vector_store_cache:
        _vector_store_cache[cache_key] = FAISS.load_local(
            str(persist_path), embeddings, allow_dangerous_deserialization=True
        )
        print(f"[Cache MISS] Loaded vector store from disk: {persist_path}")
    else:
        print(f"[Cache HIT] Using in-memory vector store for: {cache_key}")
    return _vector_store_cache[cache_key]

def _invalidate_cache(batch_dir: str):
    """Call this after adding new documents so cache is refreshed."""
    doc_key = f"{batch_dir}:doc"
    chat_key = f"{batch_dir}:chat"
    _vector_store_cache.pop(doc_key, None)
    _vector_store_cache.pop(chat_key, None)


def load_or_create_vector_store(filepath: Path):
    batch_path = filepath

    # Create faiss_index subdirectory inside the batch directory
    persist_path_doc = batch_path / "faiss_index_doc"
    persist_path_chat = batch_path / "faiss_index_chat"

    # Load PDFs from the specified directory
    loader = PyPDFDirectoryLoader(str(batch_path))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=300)
    docs = loader.load()
    chat_document = Document(
        page_content="This is a vector store for the Most relevent information of the the chat ",
        metadata={"source": "ReadWise"}
    )
    split_docs = text_splitter.split_documents(docs)
    uuids = [str(uuid4()) for _ in range(len(split_docs))]

    # Create new vector store for this batch using from_documents
    vector_store_doc = FAISS.from_documents(documents=split_docs, embedding=embeddings, ids=uuids)
    vector_store_chat = FAISS.from_documents(documents=[chat_document], embedding=embeddings, ids=["chat_init"])

    # Save the vector store in the batch's faiss_index directory
    vector_store_doc.save_local(str(persist_path_doc))
    vector_store_chat.save_local(str(persist_path_chat))
    print(f"Vector store saved to {persist_path_doc}")

    # Warm up cache immediately after creation
    _vector_store_cache[f"{str(filepath)}:doc"] = vector_store_doc
    _vector_store_cache[f"{str(filepath)}:chat"] = vector_store_chat


def get_vector_store(batch_dir: str) -> FAISS:
    batch_path = Path(batch_dir)
    persist_path = batch_path / "faiss_index_doc"
    cache_key = f"{batch_dir}:doc"
    print(f"Looking for vector store at: {persist_path}")

    if not os.path.exists(persist_path):
        load_or_create_vector_store(batch_path)

    return _get_cached(cache_key, persist_path)


def chat_vector_store(batch_dir: str) -> FAISS:
    batch_path = Path(batch_dir)
    persist_path = batch_path / "faiss_index_chat"
    cache_key = f"{batch_dir}:chat"
    print(f"Looking for vector store at: {persist_path}")

    if not os.path.exists(persist_path):
        load_or_create_vector_store(batch_path)

    return _get_cached(cache_key, persist_path)


def save_chat_vector_store(batch_dir: str, vector_store: FAISS):
    """Persist the chat vector store and update cache."""
    batch_path = Path(batch_dir)
    persist_path = batch_path / "faiss_index_chat"
    vector_store.save_local(str(persist_path))
    # Update cache so next request doesn't reload from disk
    _vector_store_cache[f"{batch_dir}:chat"] = vector_store