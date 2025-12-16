# backend/utils/chunker.py
from typing import List
import re

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks of chunk_size tokens (approx by words).
    """
    words = re.split(r"\s+", text)
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks
