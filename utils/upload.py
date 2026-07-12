from fastapi import UploadFile
from typing import List
from pathlib import Path
import uuid
import tempfile
import sys

# Safely import supabase without local namespace shadowing issues
sys.path.append(str(Path(__file__).resolve().parent.parent / "supabase"))
from supabase_client import supabase

def upload_chat_file(chat_id: int, file: UploadFile) -> str:
    file_ext = file.filename.split(".")[-1]
    storage_path = f"{chat_id}/{uuid.uuid4()}.{file_ext}"

    file.file.seek(0)
    file_bytes = file.file.read()

    supabase.storage.from_("chat-documents").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": file.content_type},
    )

    return storage_path

def download_for_processing(storage_paths: List[str]) -> Path:
    tmp_dir = Path(tempfile.mkdtemp())
    for storage_path in storage_paths:
        file_bytes = supabase.storage.from_("chat-documents").download(storage_path)
        local_path = tmp_dir / Path(storage_path).name
        local_path.write_bytes(file_bytes)
    return tmp_dir
