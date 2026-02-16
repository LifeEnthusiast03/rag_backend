from pydantic import BaseModel,EmailStr
from typing import List, Optional
from datetime import datetime

# This two model are for procesing chatRequest
class chat_his(BaseModel):
    role:str
    content:str
class ChatRequest(BaseModel):
    chat_id: int
    question: str
    chat_history: List[chat_his]

# This model is for generating token
class token_payload(BaseModel):
     userid:int

# These model is processing create/signup user request
class create_user_request(BaseModel):
        user_name:str
        email:EmailStr
        password:str
class create_user_response(BaseModel):
      user_id:int
      user_name:str
      email:EmailStr

#These models are used from procesing login user request
class login_user_request(BaseModel):
        email:EmailStr
        password:str
class login_user_response(BaseModel):
        user_id:int
        user_name:str
        email:EmailStr
        token:str
class userdataforapi(BaseModel):
      user_id:int
      user_name:str
      email:EmailStr

class chat(BaseModel):
      chat_id:int
      chat_name:str
class message(BaseModel):
      role:str
      content:str

# Model for LangChain Pydantic Output Parser - LLM structured response
class LLMResponseFormat(BaseModel):
      """Structured format for LLM responses using Pydantic Output Parser"""
      answer: str
      key_points: List[str]
      confidence_level: str  # "high", "medium", "low"
      sources_cited: Optional[List[str]] = None
      needs_clarification: bool = False
      clarification_needed: Optional[str] = None
      follow_up_suggestions: Optional[List[str]] = None
      
      class Config:
            json_schema_extra = {
                  "example": {
                        "answer": "Python is a high-level programming language known for its simplicity and readability.",
                        "key_points": [
                              "Python is interpreted and dynamically typed",
                              "Widely used for web development, data science, and automation",
                              "Has extensive standard library and third-party packages"
                        ],
                        "confidence_level": "high",
                        "sources_cited": ["Introduction to Python - Chapter 1", "Python Documentation"],
                        "needs_clarification": False,
                        "clarification_needed": None,
                        "follow_up_suggestions": [
                              "What are Python's main advantages?",
                              "How does Python compare to other languages?"
                        ]
                  }
            }

# Comprehensive chat response format for LLM output
class ChatResponse(BaseModel):
      success: bool
      chat_id: int
      response: str
      role: str = "assistant"
      timestamp: Optional[str] = None
      sources_used: Optional[int] = None
      error_message: Optional[str] = None
      
      class Config:
            json_schema_extra = {
                  "example": {
                        "success": True,
                        "chat_id": 1,
                        "response": "Based on the context provided, here is the answer...",
                        "role": "assistant",
                        "timestamp": "2026-02-13T10:30:00",
                        "sources_used": 5,
                        "error_message": None
                  }
            }
