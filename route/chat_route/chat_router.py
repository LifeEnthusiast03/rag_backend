from fastapi import APIRouter,Depends,HTTPException
from models.pymodel import ChatRequest, ChatResponse, LLMResponseFormat
from llm.chatmodel import get_response
from typing import Annotated
from models.pymodel import userdataforapi
from utils.protectroute import get_current_user
from sqlalchemy.orm import Session
from db.config import init_db
from db.data_models import Chat,Message
from models.pymodel import chat,message
from datetime import datetime
import os
import shutil
import json
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
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
        
        # Get structured response from LLM
        llm_response: LLMResponseFormat = await get_response(req,curchat_fileloc)
        if not llm_response:
            raise Exception("Failed to generate response")
        
        # Store the main answer in database
        systemmessage = Message(
            chat_id = req.chat_id,
            role="assistant",
            content=llm_response.answer  # Store the answer text
        ) 
        db.add(systemmessage)
        db.commit()
        
        # Return comprehensive response with all structured data
        return ChatResponse(
            success=True,
            chat_id=req.chat_id,
            response=json.dumps(llm_response.dict(), ensure_ascii=False, indent=2),  # Full structured response as JSON
            role="assistant",
            timestamp=datetime.now().isoformat(),
            sources_used=len(llm_response.sources_cited) if llm_response.sources_cited else 0,
            error_message=None
        )
    except Exception as e:
        db.rollback()
        print(f"Chat error: {e}")
        return ChatResponse(
            success=False,
            chat_id=req.chat_id,
            response="",
            role="assistant",
            timestamp=datetime.now().isoformat(),
            sources_used=None,
            error_message=str(e)
        )
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

@router.delete("/deletechat")
def deletechat(chatid:int,user:Annotated[userdataforapi,Depends(get_current_user)],db:Annotated[Session,Depends(init_db)]):
    try:
        # Verify chat belongs to user before deletion
        chat_to_delete = db.query(Chat).filter(Chat.chat_id==chatid, Chat.user_id==user.user_id).first()
        if not chat_to_delete:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")
        
        # Delete all messages in the chat
        db.query(Message).filter(Message.chat_id==chatid).delete(synchronize_session=False)
        
        # Delete the specific chat folder (e.g., uploads\20260212_202651)
        # Safety check: ensure we're not deleting the entire uploads folder
        if os.path.exists(chat_to_delete.chat_fileloc):
            folder_path = chat_to_delete.chat_fileloc
            folder_name = os.path.basename(folder_path)
            parent_folder = os.path.basename(os.path.dirname(folder_path))
            
            # Only delete if it's a subfolder inside uploads, not the uploads folder itself
            if parent_folder == "uploads" and folder_name and folder_name != "uploads":
                shutil.rmtree(folder_path)
            else:
                print(f"Warning: Skipping deletion of unexpected path: {folder_path}")
        
        # Delete the chat record
        db.delete(chat_to_delete)
        db.commit()
        print("delete chat successful")
        return {
            "Successful":True,
            "message":"Chat deleted successfully"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Failed to delete chat: {e}")
        return {
            "Successful":False,
            "message":"Failed to delete chat"
        }

