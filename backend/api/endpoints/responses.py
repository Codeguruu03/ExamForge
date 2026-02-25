"""
POST /api/responses/upload
────────────────────────────────────────────────────────────────────────────────
Accepts:
  - A structured Exam JSON (paste or from /api/upload/)
  - A CSV file of student responses (wide or long format)
  - A correct_answers JSON map: {question_id: correct_label}

Returns:
  ExamStats (full CTT analysis — difficulty, discrimination, alpha, flagged Qs)

This is the endpoint that closes the loop:
  Upload exam → Parse questions → Upload student CSV → Get CTT stats
"""

from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from pydantic import BaseModel
import json
from typing import Dict

from backend.core.models import Exam
from backend.core.stat_models import ExamStats
from backend.services.response_parser import parse_response_csv
from backend.services.stats_engine import StatisticalEngine

router = APIRouter()


@router.post("/upload", response_model=ExamStats)
async def upload_responses(
    exam_json: str = Form(..., description="JSON string of the Exam object"),
    correct_answers_json: str = Form(..., description="JSON map: {question_id: correct_label}"),
    file: UploadFile = File(..., description="CSV file of student responses"),
):
    """
    Full CTT analysis from a student response CSV.

    **exam_json** — paste the `exam` field from a /api/upload/ response  
    **correct_answers_json** — e.g. `{"1": "C", "2": "A", "3": "B"}`  
    **file** — CSV in wide or long format (see /docs for examples)
    """
    # ── Validate file ─────────────────────────────────────────────────────────
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    # ── Parse exam ────────────────────────────────────────────────────────────
    try:
        exam = Exam(**json.loads(exam_json))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid exam_json: {e}")

    # ── Parse correct answers ─────────────────────────────────────────────────
    try:
        correct_answers: Dict[str, str] = json.loads(correct_answers_json)
        correct_answers = {str(k): str(v).strip().upper() for k, v in correct_answers.items()}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid correct_answers_json: {e}")

    # ── Parse CSV ─────────────────────────────────────────────────────────────
    try:
        content = await file.read()
        student_responses = parse_response_csv(content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"CSV parse error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV read error: {e}")

    if len(student_responses) < 2:
        raise HTTPException(
            status_code=422,
            detail=f"Need at least 2 student rows for analysis. Found {len(student_responses)}."
        )

    # ── Run CTT engine ────────────────────────────────────────────────────────
    try:
        stats = StatisticalEngine.analyze(
            exam=exam,
            student_responses=student_responses,
            correct_answers=correct_answers,
        )
        return stats
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {e}")
