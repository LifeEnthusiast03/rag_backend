from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
from pathlib import Path
from datetime import datetime
from  fas import load_or_create_vector_store,get_vector_store
from pymodel import ChatRequest
from chatmodel import get_response
app = FastAPI()

# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "PDF Upload API is running"}

@app.post("/upload-pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
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
    
    # Load or create vector store after all files are uploaded
    if uploaded_files:
        try:
            print("entered here")
            load_or_create_vector_store(batch_dir)
            print("here fassi index will be generated in future")
        except Exception as e:
            print(e)
            return {
                "message": f"Files uploaded but vector store update failed: {str(e)}",
                "files": uploaded_files,
                "chat_id": timestamp,
                "errors": errors
            }
    
    if not uploaded_files and errors:
        raise HTTPException(status_code=400, detail=f"No files uploaded. Errors: {', '.join(errors)}")
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
        "files": uploaded_files,
        "chat_id": timestamp,
        "errors": errors if errors else None
    }
@app.post("/chat")
def pdfchat(req: ChatRequest):
    response = get_response(req)
    return {"response": response}
@app.get("/health")
def cheak_health():
    return {"health":"okay"}
