# backend/main.py
import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

from app.utils.extractor import extract_text_from_file
from app.utils.chunker import chunk_text
from app.utils.embedder import EmbeddingIndex
from app.utils.generation import summarize_textrank
from app.utils.vectorstore import answer_question_from_context
from app.utils.quizmaker import generate_quiz_from_text
import nltk
nltk.data.path.append(r"C:\Users\peaky\AppData\Roaming\nltk_data")


UPLOAD_DIR = Path("uploads")
DATA_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="SmartCampus Assistant API")

# allow CORS from Streamlit frontend (default port 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# persistent index and doc store (in-memory for runtime, on-disk for reload)
INDEX_PATH = DATA_DIR / "index.npz"
DOC_META_PATH = DATA_DIR / "doc_meta.json"

# Global in-memory holder for current file
CURRENT = {
    "file_id": None,
    "filename": None,
    "text": None,
    "chunks": None,
    "summary": None,
    "index": None  # EmbeddingIndex instance
}

# Helper models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5

class QuizRequest(BaseModel):
    num_questions: int = 5

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a single file. If a previous file exists, it will be cleared.
    Automatic processing includes: text extraction, chunking, embedding, summary.
    """
    # clear old uploads
    for p in UPLOAD_DIR.glob("*"):
        try:
            p.unlink()
        except Exception:
            if p.is_dir():
                shutil.rmtree(p)

    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    dest = UPLOAD_DIR / filename
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)

    # extract text
    try:
        raw_text = extract_text_from_file(dest)
        if not raw_text or len(raw_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="No text found in file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}")

    # chunk text (for retrieval)
    chunks = chunk_text(raw_text, chunk_size=600, overlap=80)

    # build embeddings index (uses sentence-transformers small model CPU)
    emb_index = EmbeddingIndex()
    emb_index.add_texts(chunks)

    # summarize (Textrank extractive)
    summary_points = summarize_textrank(raw_text, sentences_count=8)

    # persist basic meta (optional minimal on-disk)
    meta = {
        "file_id": file_id,
        "filename": file.filename,
        "num_chunks": len(chunks)
    }
    with open(DOC_META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # store in global
    CURRENT.update({
        "file_id": file_id,
        "filename": file.filename,
        "text": raw_text,
        "chunks": chunks,
        "summary": summary_points,
        "index": emb_index
    })

    return {"status": "ok", "file_id": file_id, "filename": file.filename, "summary_points": summary_points}

@app.get("/summary")
def get_summary():
    if not CURRENT.get("file_id"):
        raise HTTPException(status_code=404, detail="No file uploaded yet.")
    return {"file_id": CURRENT["file_id"], "filename": CURRENT["filename"], "summary": CURRENT["summary"]}

@app.post("/query")
def query(qr: QueryRequest):
    if not CURRENT.get("file_id"):
        raise HTTPException(status_code=404, detail="No file uploaded yet.")
    answer, used_chunks = answer_question_from_context(
        qr.question,
        CURRENT["chunks"],
        CURRENT["index"],
        top_k=qr.top_k
    )
    return {"question": qr.question, "answer": answer, "used_chunks": used_chunks}

@app.post("/quiz")
def quiz(qr: QuizRequest):
    if not CURRENT.get("file_id"):
        raise HTTPException(status_code=404, detail="No file uploaded yet.")
    quiz = generate_quiz_from_text(CURRENT["text"], qr.num_questions)
    # quiz: list of {"question":..., "options":[...], "answer": index}
    return {"quiz": quiz}

@app.get("/status")
def status():
    if not CURRENT.get("file_id"):
        return {"status": "no_file"}
    return {
        "status": "ready",
        "file_id": CURRENT["file_id"],
        "filename": CURRENT["filename"],
        "num_chunks": len(CURRENT["chunks"]),
        "summary_count": len(CURRENT["summary"]) if CURRENT["summary"] else 0
    }
