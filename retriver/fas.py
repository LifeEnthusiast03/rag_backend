from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from uuid import uuid4
from langchain_community.vectorstores import FAISS
from pathlib import Path
import os


# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
def load_or_create_vector_store(filepath:Path):
    
    batch_path = filepath
    
    # Create faiss_index subdirectory inside the batch directory
    persist_path = batch_path / "faiss_index"
    
    # Load PDFs from the specified directory
    loader = PyPDFDirectoryLoader(str(batch_path))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=300)
    docs = loader.load()
     
    split_docs = text_splitter.split_documents(docs)
    uuids = [str(uuid4()) for _ in range(len(split_docs))]
            
    # Create new vector store for this batch using from_documents
    vector_store = FAISS.from_documents(documents=split_docs, embedding=embeddings, ids=uuids)
    
    # Save the vector store in the batch's faiss_index directory
    vector_store.save_local(str(persist_path))
    print(f"Vector store saved to {persist_path}")


def get_vector_store(batch_dir:str):
    # Construct full path with uploads directory
    batch_path = Path(batch_dir)
    persist_path = batch_path / "faiss_index"
    print(f"Looking for vector store at: {persist_path}")
    
    if os.path.exists(persist_path):
        print("entered here")
        vector_store = FAISS.load_local(str(persist_path), embeddings, allow_dangerous_deserialization=True)
    else:
        load_or_create_vector_store(batch_path)
        vector_store = FAISS.load_local(str(persist_path), embeddings, allow_dangerous_deserialization=True)
    print(f"success full geting the vector store")
    return vector_store