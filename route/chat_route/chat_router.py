from fastapi import APIRouter,Depends
from models.pymodel import ChatRequest
from llm.chatmodel import get_response
from typing import Annotated
from models.pymodel import userdataforapi
from utils.protectroute import get_current_user
from sqlalchemy.orm import Session
from db.config import init_db
from db.data_models import Chat,Message
from models.pymodel import chat,message
router = APIRouter()

@router.post("/chat")
async def pdfchat(req: ChatRequest,user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
    try:
        cur_chat = db.query(Chat).filter(Chat.chat_id==req.chat_id, Chat.user_id==user.user_id).first()
        if not cur_chat:
            raise Exception("Chat not found or access denied")
        usermessage = Message(
            chat_id=req.chat_id,
            role="user",
            content=req.question
        )
        db.add(usermessage)
        db.commit()
        curchat_fileloc =cur_chat.chat_fileloc
        response = await get_response(req,curchat_fileloc)
        if not response:
            raise Exception("failed to generate response")
        systemmessage = Message(
            chat_id = req.chat_id,
            role="system",
            content=response
        ) 
        db.add(systemmessage)
        db.commit()
        return {"response": response,
                "Successful":True}
    except Exception as e:
        db.rollback()
        print(f"Chat error: {e}")
        return {"response": str(e),
                "Successful":False}
@router.get("/getchat")
def getchat(user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
     try:
        print("going to get the chat")
        chats = db.query(Chat).filter(Chat.user_id==user.user_id).all()
        if chats :
            print("yeah i got the chats")
        userchats=[]
        for c in chats:
            userchats.append(chat(chat_id=int(c.chat_id), chat_name=str(c.chat_name)))
        return {"chats": userchats,
                "Successful":True}
     except Exception as e:
         print(f"Failed to fetch chat {e}")
         return {"chats": [],
                 "Successful":False}
         
@router.get("/getchatconversation")
def getchatconversation(chatid:int,user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
    try:
        # Verify chat belongs to user
        chat_exists = db.query(Chat).filter(Chat.chat_id==chatid, Chat.user_id==user.user_id).first()
        if not chat_exists:
            raise Exception("Chat not found or access denied")
        messages = db.query(Message).filter(Message.chat_id==chatid).order_by(Message.message_id).all();
        chatmessage = []
        for m in messages:
            chatmessage.append(message(role=m.role,content=m.content))
        return {
            "messages":chatmessage,
            "Successful":True
        }
    except Exception as e:
        print(f"Failed to fetch chat message: {e}")
        return {
            "messages":[],
            "error": str(e),
            "Successful":False
        }

