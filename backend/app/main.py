from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI()

UPLOAD_DIR = "uploads"

origins = [
    "http://localhost:5173",   # frontend dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Create directory for uploads (static for now, later user_id based)
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # Save file path
    file_id = datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save file contents
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Return metadata
    return {
        "file_id": file_id,
        "filename": file.filename,
        "saved_as": save_path,
        "size_kb": round(os.path.getsize(save_path) / 1024, 2)
    }
