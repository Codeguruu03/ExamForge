from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.core.models import Exam
from backend.core.similarity_models import SimilarityReport
from backend.services.similarity_engine import SimilarityEngine


class SimilarityRequest(BaseModel):
    exam: Exam


router = APIRouter()


@router.post("/", response_model=SimilarityReport)
async def detect_similarity(body: SimilarityRequest):
    """
    Phase 4 — Similarity & Redundancy Detection Endpoint.

    Accepts a structured Exam (output from Phase 2 Normalization).
    Returns a SimilarityReport identifying:
      - Exact duplicate questions (similarity ≥ 0.95)
      - Near-duplicate / paraphrased questions (0.60 ≤ sim < 0.95)
      - Similarity clusters (grouped by union-find)
      - Count of unique questions (not in any cluster)
    """
    if not body.exam.questions:
        raise HTTPException(status_code=400, detail="Exam has no questions to analyze.")
    if len(body.exam.questions) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 questions are required for similarity analysis."
        )

    try:
        report = SimilarityEngine.analyze(body.exam.questions)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity analysis failed: {str(e)}")
