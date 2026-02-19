from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from backend.services.stats_engine import StatisticalEngine
from backend.core.stat_models import ExamStats
from backend.core.models import Exam, Question, Option


# ─── Request schema ───────────────────────────────────────────────────────────

class StudentResponse(BaseModel):
    student_id: str
    responses: Dict[str, str]    # {question_id (str): chosen_label (str)}


class AnalyzeRequest(BaseModel):
    exam: Exam
    student_responses: List[StudentResponse]
    correct_answers: Dict[str, str]   # {question_id (str): correct_label (str)}


# ─── Router ───────────────────────────────────────────────────────────────────

router = APIRouter()


@router.post("/", response_model=ExamStats)
async def analyze_exam(body: AnalyzeRequest):
    """
    Phase 3 — Statistical Analysis Endpoint.

    Accepts:
      - A structured exam (output from Phase 2 normalization)
      - Student response data
      - Correct answers map

    Returns a full ExamStats report with:
      - Difficulty Index per question
      - Discrimination Index per question
      - Distractor Efficiency per option
      - Cronbach's Alpha (reliability)
      - Flagged questions with reasons
    """
    if not body.student_responses:
        raise HTTPException(status_code=400, detail="No student responses provided.")
    if len(body.student_responses) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 student responses are required for statistical analysis."
        )
    if not body.correct_answers:
        raise HTTPException(status_code=400, detail="No correct answers provided.")

    try:
        stats = StatisticalEngine.analyze(
            exam=body.exam,
            student_responses=[sr.model_dump() for sr in body.student_responses],
            correct_answers=body.correct_answers,
        )
        return stats
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
