from pathlib import Path
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from sqlalchemy import select
from langchain_community.document_loaders import PyPDFDirectoryLoader
from typing import Annotated
from db.data_models import DocumentChunk
from db.config import init_db
from retriver.embedding import embeddings
from retriver.text_spilter import text_splitter
from fastapi import Depends
async def add_vector_to_db(chat_id: int, filepath: Path,db:Annotated[Session,Depends(init_db)]):
    try:
        print("vector upload started ")
        loader = PyPDFDirectoryLoader(filepath)
        docs = loader.load()
        split_docs = text_splitter.split_documents(docs)

        texts = [d.page_content for d in split_docs]
        vectors = embeddings.embed_documents(texts)
        for doc, vector in zip(split_docs, vectors):
            db.add(DocumentChunk(
                chat_id=chat_id,
                content=doc.page_content,
                doc_metadata=doc.metadata,
                embedding=vector,
            ))
        db.commit()
        print("vector upload complete")
    finally:
        db.close()  