# backend/utils/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class EmbeddingIndex:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        # small, fast model for CPU
        self.model = SentenceTransformer(model_name)
        self.texts = []
        self.embeddings = None

    def add_texts(self, texts: List[str]):
        self.texts = texts
        self.embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    def query(self, query_text: str, top_k: int = 5):
        q_emb = self.model.encode([query_text], show_progress_bar=False, convert_to_numpy=True)
        sims = cosine_similarity(q_emb, self.embeddings)[0]
        idxs = sims.argsort()[::-1][:top_k]
        results = [(int(i), float(sims[i]), self.texts[i]) for i in idxs]
        return results
