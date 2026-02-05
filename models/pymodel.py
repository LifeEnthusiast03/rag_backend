from pydantic import BaseModel
from typing import List
class chat_his(BaseModel):
    role:str
    content:str
class ChatRequest(BaseModel):
    chat_id: str
    question: str
    chat_history: List[chat_his]

class token_payload(BaseModel):
     userid:int