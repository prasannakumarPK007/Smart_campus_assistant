
---

# 🎓 Smart Campus Assistant

A **lightweight, CPU-friendly Smart Campus Assistant** that allows users to **upload academic documents**, get **automatic summaries**, ask **context-aware questions**, and generate **interactive quizzes** — all using **free and fast open-source models**.

---

## 🚀 Features

### 📂 1. Document Upload & Processing

* Upload **one file at a time** (PDF / TXT)
* Automatically clears the previous document
* Extracts and processes content instantly

### 📝 2. Automatic Summarization

* Generates **point-wise summaries**
* Uses **TextRank-based summarization**
* Fast, offline, and CPU-friendly

### ❓ 3. Context-Aware Q&A

* Ask questions based on uploaded material
* Answers are generated **only from source content**
* Uses semantic search + embeddings (FAISS)

### 🧠 4. Quiz Generator

* User chooses number of questions
* Generates **MCQs with options**
* Answers are hidden initially
* “Show Answer” option for self-assessment

---

## 🏗️ Project Structure

```
Project_Smart_Camp/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── utils/
│   │       ├── extractor.py
│   │       ├── generation.py
│   │       ├── quizmaker.py
│   │       └── embeddings.py
│   ├── uploads/
│   ├── extracted/
│   ├── vectors/
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── app.py
│   ├── summarizer.py
│   ├── venv_frontend/
│   └── requirements.txt
│
└── README.md
```

---

## ⚙️ Tech Stack

### Backend

* **FastAPI**
* **FAISS** (Vector Search)
* **NLTK**
* **Sumy (TextRank)**
* **Sentence Transformers**
* **CPU-only, free models**

### Frontend

* **Streamlit**
* **Requests**
* **Professional UI with tabs & cards**

---

## 📦 Model Used

* **amazon/nova-2-lite-v1**

  * Lightweight
  * CPU-friendly
  * Cost-free
  * Fast inference

---

## 🔧 Backend Setup

### 1️⃣ Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### 2️⃣ Activate Environment

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Download NLTK Resources

```bash
python -m nltk.downloader punkt
python -m nltk.downloader punkt_tab
python -m nltk.downloader averaged_perceptron_tagger_eng
```

### 5️⃣ Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will run at:

```
http://localhost:8000
```

---

## 🎨 Frontend Setup (Streamlit)

### 1️⃣ Create Frontend Environment

```bash
cd frontend
python -m venv venv_frontend
```

### 2️⃣ Activate Environment

```bash
.\venv_frontend\Scripts\Activate.ps1
```

### 3️⃣ Install Frontend Packages

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Streamlit App

```bash
streamlit run app.py
```

Frontend will open at:

```
http://localhost:8501
```

---

## 🔌 Backend API Endpoints

| Endpoint  | Method | Description                 |
| --------- | ------ | --------------------------- |
| `/upload` | POST   | Upload document & summarize |
| `/query`  | POST   | Ask questions from document |
| `/quiz`   | POST   | Generate MCQ quiz           |

---

## 🔒 Constraints & Rules

* Only **one file** allowed at a time
* New upload clears previous data
* Answers are strictly based on uploaded content
* Fully **offline & CPU-based**

---

## 🎯 Use Cases

* Smart Campus Assistants
* Academic Document Analysis
* Student Self-Assessment
* College Projects & Final Year Submissions
* AI-powered Learning Systems

---

## 🏁 Status

✅ Backend working
✅ Frontend working
✅ Error-free pipeline
✅ Ready for demo & evaluation

---
