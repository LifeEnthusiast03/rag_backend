from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4
from pathlib import Path
import os


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
def load_or_create_vector_store(filepath:Path):
    
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
        metadata={"source":"ReadWise"}
    )
    split_docs = text_splitter.split_documents(docs)
    uuids = [str(uuid4()) for _ in range(len(split_docs))]
            
    # Create new vector store for this batch using from_documents
    vector_store_doc = FAISS.from_documents(documents=split_docs, embedding=embeddings, ids=uuids)
    # Fixed: documents must be a list, ids must be a list
    vector_store_chat = FAISS.from_documents(documents=[chat_document], embedding=embeddings, ids=["chat_init"])
    # Save the vector store in the batch's faiss_index directory
    vector_store_doc.save_local(str(persist_path_doc))
    vector_store_chat.save_local(str(persist_path_chat))
    print(f"Vector store saved to {persist_path_doc}")


def get_vector_store(batch_dir:str):
    # Construct full path with uploads directory
    batch_path = Path(batch_dir)
    persist_path = batch_path / "faiss_index_doc"
    print(f"Looking for vector store at: {persist_path}")
    
    if os.path.exists(persist_path):
        print("entered here")
        vector_store = FAISS.load_local(str(persist_path), embeddings, allow_dangerous_deserialization=True)
    else:
        load_or_create_vector_store(batch_path)
        vector_store = FAISS.load_local(str(persist_path), embeddings, allow_dangerous_deserialization=True)
    print(f"Successfully getting the vector store")
    return vector_store
def chat_vector_store(batch_dir:str):
    batch_path = Path(batch_dir)
    persist_path = batch_path / "faiss_index_chat"
    print(f"Looking for vector store at: {persist_path}")
    
    if os.path.exists(persist_path):
        print("entered here")
        vector_store = FAISS.load_local(str(persist_path), embeddings, allow_dangerous_deserialization=True)
    else:
        load_or_create_vector_store(batch_path)
        vector_store = FAISS.load_local(str(persist_path), embeddings, allow_dangerous_deserialization=True)
    print(f"Successfully getting the vector store")
    return vector_store