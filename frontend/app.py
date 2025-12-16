# frontend/app.py
import streamlit as st
import requests
from summarizer import render_upload_and_summary
from typing import List

# --- Configuration ---
DEFAULT_API_BASE = "http://localhost:8000"
API_BASE = DEFAULT_API_BASE   # <- FIXED (no st.secrets)


st.set_page_config(page_title="SmartCampus Assistant", layout="wide", initial_sidebar_state="expanded")

# --- Sidebar: status and config ---
with st.sidebar:
    st.header("SmartCampus Assistant")
    st.write("Frontend connected to backend at:")
    st.code(API_BASE)
    if st.button("Check backend status"):
        try:
            r = requests.get(f"{API_BASE}/status", timeout=6)
            r.raise_for_status()
            jd = r.json()
            st.success("Backend reachable")
            st.json(jd)
        except Exception as e:
            st.error("Backend not reachable:")
            st.write(e)

    st.markdown("---")
    st.caption("Created for Smart Campus Assistant · Upload → Summary → Q&A → Quiz")

# --- Page header ---
st.title("SmartCampus Assistant")
st.subheader("Upload material, ask questions, and generate quizzes — all powered by your backend")

# --- Top: Upload & Summary (left column) ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 1) Upload & Summary")
    # summarizer module handles upload and displays summary
    uploaded_meta = render_upload_and_summary(API_BASE)

    # uploaded_meta is None if no file, otherwise dict from backend
    if uploaded_meta:
        st.success(f"Current file: {uploaded_meta.get('filename')}")
    else:
        st.info("No file uploaded. Upload a file to enable Q&A and Quiz.")

with col2:
    st.markdown("### 2) Quick Actions & Backend Info")
    st.markdown("Use the panels below to interact with the processed file.")
    # quick status box
    try:
        r = requests.get(f"{API_BASE}/status", timeout=5)
        if r.status_code == 200:
            status = r.json()
            st.metric("Backend status", status.get("status", "unknown"))
            st.write("File:", status.get("filename", "—"))
            st.write("Chunks:", status.get("num_chunks", "—"))
        else:
            st.warning("No file processed yet or backend returned non-200.")
    except Exception:
        st.warning("Could not connect to backend for status. Make sure backend is running on port 8000.")

st.markdown("---")

# --- Q&A and Quiz in tabs (same page) ---
tab1, tab2 = st.tabs(["Q & A", "Quiz"])

# Helper to check if a file exists on backend
def backend_has_file(api_base: str) -> bool:
    try:
        r = requests.get(f"{api_base}/status", timeout=5)
        if r.status_code == 200:
            j = r.json()
            return j.get("status") == "ready"
        return False
    except Exception:
        return False

HAS_FILE = backend_has_file(API_BASE)

# ---- Q&A tab ----
with tab1:
    st.header("Ask questions about the uploaded file")
    if not HAS_FILE:
        st.info("Upload a file first (left panel).")
    else:
        question = st.text_area("Enter your question", height=80)
        top_k = st.slider("Context chunks to use (top K)", min_value=1, max_value=8, value=4)
        ask_btn = st.button("Ask")

        if ask_btn:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Querying the backend..."):
                    try:
                        resp = requests.post(f"{API_BASE}/query", json={"question": question, "top_k": top_k}, timeout=30)
                        resp.raise_for_status()
                        res = resp.json()
                        st.subheader("Answer")
                        st.write(res.get("answer", "No answer returned."))
                        used = res.get("used_chunks", [])
                        if used:
                            with st.expander("Show source chunks used (for traceability)"):
                                for u in used:
                                    score = u.get("score", 0)
                                    text = u.get("text", "")
                                    st.markdown(f"- **score:** {score:.3f} — {text[:800]}{'...' if len(text) > 800 else ''}")
                        else:
                            st.caption("No source chunks returned.")
                    except Exception as e:
                        st.error("Query failed.")
                        st.exception(e)

# ---- Quiz tab ----
with tab2:
    st.header("Generate a Quiz from the uploaded file")
    if not HAS_FILE:
        st.info("Upload a file first (left panel).")
    else:
        st.markdown("Choose number of questions and generate a multiple-choice quiz. Answers are hidden — click 'Show Answer' per question.")
        n_q = st.number_input("Number of questions", min_value=1, max_value=30, value=5)
        gen_btn = st.button("Generate Quiz")

        if gen_btn:
            with st.spinner("Generating quiz..."):
                try:
                    resp = requests.post(f"{API_BASE}/quiz", json={"num_questions": int(n_q)}, timeout=60)
                    resp.raise_for_status()
                    jd = resp.json()
                    quiz = jd.get("quiz", [])
                    if not quiz:
                        st.warning("No quiz items returned.")
                    else:
                        st.success(f"Generated {len(quiz)} questions")
                        # store in session state for persistent selection and show-answer toggles
                        st.session_state["current_quiz"] = quiz
                        st.session_state["show_answer_flags"] = [False] * len(quiz)
                except Exception as e:
                    st.error("Failed to generate quiz.")
                    st.exception(e)

        # display quiz if present in session_state
        quiz = st.session_state.get("current_quiz", None)
        if quiz:
            for idx, item in enumerate(quiz):
                st.markdown(f"**Q{idx+1}.** {item.get('question')}")
                options = item.get("options", [])
                # show radio with a unique key per question to keep selection state
                choice_key = f"quiz_choice_{idx}"
                st.radio(f"Select answer for Q{idx+1}", options=options, key=choice_key, index=0)
                # Show Answer button
                colL, colR = st.columns([1, 8])
                with colL:
                    if st.button(f"Show Answer Q{idx+1}", key=f"show_btn_{idx}"):
                        st.session_state["show_answer_flags"][idx] = True
                with colR:
                    if st.session_state["show_answer_flags"][idx]:
                        correct_idx = item.get("answer_index", 0)
                        correct = options[correct_idx] if 0 <= correct_idx < len(options) else "Unknown"
                        st.info(f"**Answer:** {correct}")

st.markdown("---")
st.caption("SmartCampus Assistant — Frontend (Streamlit). Backend API routes: /upload, /summary, /query, /quiz, /status")
