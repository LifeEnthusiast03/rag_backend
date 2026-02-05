from fastapi import APIRouter
from models.pymodel import ChatRequest
from llm.chatmodel import get_response
router = APIRouter()

@router.post("/chat")
def pdfchat(req: ChatRequest):
    response = get_response(req)
    return {"response": response}

