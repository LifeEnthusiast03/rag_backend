from fastapi import APIRouter,Depends
from models.pymodel import ChatRequest
from llm.chatmodel import get_response
from typing import Annotated
from models.pymodel import userdataforapi
from utils.routeprotect import get_current_user
from sqlalchemy.orm import Session
from db.config import init_db
from db.data_models import Chat,Message
from models.pymodel import chat,message
router = APIRouter()

@router.post("/chat")
async def pdfchat(req: ChatRequest,user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
    usermessage = Message(
        chat_id=req.chat_id,
        role="user",
        content=req.question
    )
    db.add(usermessage)
    db.commit()
    response = await get_response(req)
    systemmessage = Message(
        chat_id = req.chat_id,
        role="system",
        content=response
    ) 
    db.add(systemmessage)
    db.commit()
    return {"response": response}
@router.get("/getchat")
def getchat(user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
     try:
        chats = db.query(Chat).filter(Chat.user_id==user.user_id).all()
        userchats=[]
        for c in chats:
            userchats.append(chat(chat_id=c.chat_id, chat_name=c.chat_name))
        return {"chats": userchats,
                "Successful":True}
     except Exception as e:
         print(f"Failed to fetch chat {e}")
         return {"chats": [],
                 "Successful":False}
         
@router.get("/getchatconversation")
def getchatconversation(chatid:int,user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
    try:
        messages = db.query(Message).filter(Message.chat_id==chatid).order_by(Message.message_id).all();
        chatmessage = []
        for m in messages:
            chatmessage.append(message(role=m.role,content=m.content))
        return {
            "messages":chatmessage,
            "Successful":True
        }
    except Exception as e:
        print(f"failed to fetch chat message{e}")
        return {
            "messages":[],
            "Successful":False
        }

