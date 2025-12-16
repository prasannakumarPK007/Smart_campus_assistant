# backend/utils/qa_utils.py
import os
from typing import List, Tuple
from .embedder import EmbeddingIndex

HF_TOKEN = os.environ.get("HF_API_TOKEN", None)
GEN_MODEL = os.environ.get("amazon/nova-2-lite-v1", None)  # e.g. "amazon/nova-2-lite-v1"

def _call_hf_generation(prompt: str, model: str, token: str, max_tokens: int = 256) -> str:
    import requests
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": 0.2, "top_k":50}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    out = resp.json()
    # inference API may return text in different formats
    if isinstance(out, dict) and "error" in out:
        raise RuntimeError(out["error"])
    if isinstance(out, list) and len(out) > 0 and "generated_text" in out[0]:
        return out[0]["generated_text"]
    # fallback
    if isinstance(out, list) and len(out) > 0:
        return out[0].get("generated_text", str(out[0]))
    return str(out)

def answer_question_from_context(question: str, chunks: List[str], index: EmbeddingIndex, top_k=5) -> Tuple[str, List[dict]]:
    """
    Retrieve top K chunks and either return concatenated chunks (extractive)
    or call generation model with prompt+context if HF_TOKEN+GEN_MODEL provided.
    """
    results = index.query(question, top_k=top_k)
    used = []
    context_texts = []
    for idx, score, text in results:
        used.append({"idx": idx, "score": score, "text": text})
        context_texts.append(text)

    context = "\n\n".join(context_texts)
    # If user provided HF token and model, call the model to generate answer (optional)
    if HF_TOKEN and GEN_MODEL:
        prompt = (
            "You are a helpful assistant. Use the CONTEXT to answer the QUESTION succinctly.\n\n"
            f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer:"
        )
        try:
            gen = _call_hf_generation(prompt, GEN_MODEL, HF_TOKEN, max_tokens=256)
            return gen.strip(), used
        except Exception as e:
            # fallback to extractive
            return (f"(generation failed: {e})\n\n" + context_texts[0], used)

    # default: extractive answer by returning the top chunk(s)
    short_answer = context_texts[0] if len(context_texts) > 0 else "No relevant information found."
    # for better answer, include small synth: list top sentences in top chunk
    return short_answer, used
