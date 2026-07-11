from fastapi import APIRouter,UploadFile, File, HTTPException,Depends
from typing import List,Annotated
import shutil
from pathlib import Path
from datetime import datetime
from retriver.vector import add_vector_to_db
from utils.protectroute import get_current_user
from sqlalchemy.orm import Session
from models.pymodel import userdataforapi
from db.config import init_db
from db.data_models import Chat
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
router = APIRouter()
@router.post("/upload-pdfs")
async def upload_pdfs(db:Annotated[Session,Depends(init_db)],user:Annotated[userdataforapi,Depends(get_current_user)],files: List[UploadFile] = File(...)):
    uploaded_files = []
    errors = []
    
    # Create a unique directory for this upload batch using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = UPLOAD_DIR / timestamp
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        # Validate file is a PDF
        if not file.filename.endswith('.pdf'):
            errors.append(f"{file.filename}: Not a PDF file")
            continue
        
        # Save the file in the batch directory
        file_path = batch_dir / file.filename
        
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file_path.stat().st_size,
                "path": str(file_path),
                "batch": timestamp
            })
            print(f"File saved: {file.filename} in batch {timestamp}")
        
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
        
        finally:
            file.file.close()
    
    # Add vectors to pgvector DB after all files are uploaded
    if uploaded_files:
        try:
            # Create chat first to get chat_id for vector storage
            newchat = Chat(
                chat_name=uploaded_files[0]["filename"],
                chat_fileloc=str(batch_dir),
                user_id=user.user_id
            )
            db.add(newchat)
            db.commit()
            db.refresh(newchat)

            # Cache these before add_vector_to_db closes the session
            chat_id = newchat.chat_id
            chat_name = newchat.chat_name

            # Now embed and store document chunks linked to this chat
            await add_vector_to_db(chat_id, batch_dir, db)

            return {
                "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
                "files": uploaded_files,
                "chat_id": chat_id,
                "chat_name": chat_name,
                "errors": errors if errors else None
            }
        except Exception as e:
            print(e)
            # Rollback database changes if vector store creation fails
            db.rollback()
            return {
                "message": f"Files uploaded but vector store update failed: {str(e)}",
                "files": uploaded_files,
                "chat_id": None,
                "chat_name":None,
                "errors": errors
            }
    
    if not uploaded_files and errors:
        raise HTTPException(status_code=400, detail=f"No files uploaded. Errors: {', '.join(errors)}")
