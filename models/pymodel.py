from pydantic import BaseModel,EmailStr
from typing import List

# This two model are for procesing chatRequest
class chat_his(BaseModel):
    role:str
    content:str
class ChatRequest(BaseModel):
    chat_id: str
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
