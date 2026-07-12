from fastapi import APIRouter,UploadFile, File, HTTPException,Depends
from typing import List,Annotated
import shutil
from pathlib import Path
from datetime import datetime
from retriver.vector import add_vector_to_db
from utils.protectroute import get_current_user
from utils.upload import upload_chat_file, download_for_processing
from sqlalchemy.orm import Session
from models.pymodel import userdataforapi
from db.config import init_db
from db.data_models import Chat

router = APIRouter()

@router.post("/upload-pdfs")
async def upload_pdfs(db:Annotated[Session,Depends(init_db)],user:Annotated[userdataforapi,Depends(get_current_user)],files: List[UploadFile] = File(...)):
    uploaded_files = []
    errors = []
    
    # Pre-validate
    valid_files = []
    for file in files:
        if not file.filename.endswith('.pdf'):
            errors.append(f"{file.filename}: Not a PDF file")
        else:
            valid_files.append(file)
            
    if not valid_files:
        raise HTTPException(status_code=400, detail=f"No valid files to upload. Errors: {', '.join(errors)}")
        
    # We need a chat_id to organize files in Supabase
    try:
        newchat = Chat(
            chat_name=valid_files[0].filename,
            chat_fileloc="pending",
            user_id=user.user_id
        )
        db.add(newchat)
        db.commit()
        db.refresh(newchat)
        chat_id = newchat.chat_id
        chat_name = newchat.chat_name
    except Exception as e:
        return {"message": f"Failed to create chat: {str(e)}", "errors": errors}

    storage_paths = []
    
    for file in valid_files:
        try:
            storage_path = upload_chat_file(chat_id, file)
            storage_paths.append(storage_path)
            
            uploaded_files.append({
                "filename": file.filename,
                "storage_path": storage_path
            })
            print(f"File saved to Supabase: {storage_path}")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
        finally:
            file.file.close()
    print("files uploaded")         
    if not storage_paths:
        # Rollback chat creation since no files uploaded successfully
        db.delete(newchat)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Failed to upload files. Errors: {', '.join(errors)}")

    # Update chat_fileloc with the directory in Supabase (which is just the chat_id)
    newchat.chat_fileloc = str(chat_id)
    db.commit()
    
    # Process files
    tmp_dir = None
    try:
        tmp_dir = download_for_processing(storage_paths)
        print("downloaded done and processing started")
        await add_vector_to_db(chat_id, tmp_dir, db)
        
        return {
            "message": f"Successfully uploaded and processed {len(storage_paths)} file(s)",
            "files": uploaded_files,
            "chat_id": chat_id,
            "chat_name": chat_name,
            "errors": errors if errors else None
        }
    except Exception as e:
        print(e)
        return {
            "message": f"Files uploaded but vector store update failed: {str(e)}",
            "files": uploaded_files,
            "chat_id": chat_id,
            "chat_name": chat_name,
            "errors": errors
        }
    finally:
        # Clean up temporary directory
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir)
