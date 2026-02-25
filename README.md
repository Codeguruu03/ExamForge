# ExamForge 🎓

**Exam Reliability & Question Quality Analyzer**  
An industry-grade tool that extracts questions from exam documents, runs Classical Test Theory (CTT) analysis, and detects duplicate questions — powered by a FastAPI backend + React frontend.

---

## Features

| Feature | Detail |
|---------|--------|
| **Document Ingestion** | PDF (text + scanned via OCR), DOCX, TXT, Images (JPG/PNG/TIFF) |
| **Normalization** | Regex-based question parser → structured JSON |
| **Difficulty Index** | p-value per question (proportion correct) |
| **Discrimination Index** | D-value using top/bottom 27% split |
| **Distractor Efficiency** | Flags non-correct options chosen by < 5% |
| **Cronbach's Alpha** | Exam-level internal consistency |
| **Similarity Detection** | TF-IDF + Cosine Similarity, union-find clustering |
| **React Dashboard** | Upload → analysis → interactive charts + question table |

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Codeguruu03/ExamForge.git
cd ExamForge
```

### 2. Backend Setup
```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OCR_SPACE_API_KEY
```

### 3. Run the API Server
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
API docs available at: `http://localhost:8000/docs`

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at: `http://localhost:5173`

---

## API Reference

### `POST /api/upload/`
Upload an exam document. Returns structured `NormalizationResult`.

**Body:** `multipart/form-data`  
**Field:** `file` — PDF, DOCX, TXT, JPG, PNG, TIFF, BMP, GIF

```json
{
  "exam": {
    "exam_id": "uuid",
    "total_questions": 25,
    "questions": [ { "id": 1, "text": "...", "options": [...], "correct_option": "C" } ]
  },
  "warnings": [],
  "raw_text_preview": "..."
}
```

---

### `POST /api/analyze/`
Run Classical Test Theory analysis on an exam with student responses.

```json
{
  "exam": { ... },
  "student_responses": [
    { "student_id": "S01", "responses": { "1": "C", "2": "A" } }
  ],
  "correct_answers": { "1": "C", "2": "B" }
}
```

Returns `ExamStats` with per-question `difficulty_index`, `discrimination_index`, `distractor` breakdown, and exam-level `cronbach_alpha`.

---

### `POST /api/similarity/`
Detect duplicate/near-duplicate questions using TF-IDF + Cosine Similarity.

```json
{ "exam": { ... } }
```

Returns `SimilarityReport` — pairs at ≥ 0.95 similarity (duplicates) and 0.60–0.94 (near-duplicates), grouped into clusters.

---

## Project Structure

```
ExamForge/
├── backend/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── upload.py       # POST /api/upload/
│   │   │   ├── analyze.py      # POST /api/analyze/
│   │   │   └── similarity.py   # POST /api/similarity/
│   │   └── router.py
│   ├── core/
│   │   ├── models.py           # Exam, Question, Option, NormalizationResult
│   │   ├── stat_models.py      # ExamStats, QuestionStat, DistractorStat
│   │   └── similarity_models.py# SimilarityReport, SimilarPair, Cluster
│   ├── services/
│   │   ├── ingestion.py        # PDF/DOCX/Image text extraction
│   │   ├── cleaner.py          # Text noise removal
│   │   ├── normalizer.py       # Regex question parser
│   │   ├── stats_engine.py     # CTT metrics engine
│   │   └── similarity_engine.py# TF-IDF similarity engine
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── UploadPage.jsx
│       │   └── Dashboard.jsx
│       └── components/
│           ├── StatsOverview.jsx
│           ├── DifficultyChart.jsx
│           ├── SimilarityReport.jsx
│           └── QuestionTable.jsx
├── .env.example
└── README.md
```

---

## Tech Stack

**Backend:** FastAPI · Uvicorn · PyMuPDF · python-docx · NumPy · scikit-learn · python-dotenv · OCR.space API  
**Frontend:** React 19 · Vite 7 · Tailwind CSS · Recharts · Axios

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OCR_SPACE_API_KEY` | ✅ | Free key from [ocr.space](https://ocr.space/ocrapi/freekey) |
| `UPLOAD_DIR` | Optional | Upload directory (default: `uploads`) |
