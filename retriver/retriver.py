from retriver.embedding import embeddings
from db.data_models import DocumentChunk
from db.config import init_db
from sqlalchemy import select
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
async def similarityretriver(question:str,chat_id:int,k:int,db:Annotated[Session,Depends(init_db)]):
    query_vector = embeddings.embed_query(question)
    results = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.chat_id == chat_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
        .limit(k)
    ).all()
    return results