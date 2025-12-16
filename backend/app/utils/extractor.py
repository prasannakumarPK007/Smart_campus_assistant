# backend/utils/extractor.py
from pathlib import Path
from typing import Optional
import io

def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def _read_docx(path: Path) -> str:
    try:
        import docx
    except ImportError:
        raise RuntimeError("python-docx is required for .docx reading (pip install python-docx)")
    doc = docx.Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)

def _read_pdf(path: Path) -> str:
    # lightweight: use PyPDF2
    try:
        import PyPDF2
    except ImportError:
        raise RuntimeError("PyPDF2 required (pip install PyPDF2)")
    text = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                text.append(txt)
    return "\n".join(text)

def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in [".txt"]:
        return _read_txt(path)
    elif suffix in [".docx"]:
        return _read_docx(path)
    elif suffix in [".pdf"]:
        return _read_pdf(path)
    else:
        # attempt to read as txt
        return _read_txt(path)
