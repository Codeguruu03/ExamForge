"""
Extended Pydantic models for Statistical Analysis Engine (Phase 3).
These augment the base models from core/models.py with stats result types.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict


class DistractorStat(BaseModel):
    label: str              # "A", "B", "C", "D"
    text: str
    chosen_count: int       # how many students chose this option
    chosen_pct: float       # percentage
    is_correct: bool
    is_effective: bool      # True if chosen by ≥5% of students (non-correct only)


class QuestionStat(BaseModel):
    question_id: int
    question_text: str
    difficulty_index: float         # p-value: proportion who answered correctly (0–1)
    difficulty_label: str           # "Easy", "Moderate", "Hard"
    discrimination_index: float     # D-value: top27% correct – bottom27% correct
    discrimination_label: str       # "Excellent", "Good", "Fair", "Poor", "Remove"
    distractors: List[DistractorStat] = []
    is_flagged: bool = False
    flag_reasons: List[str] = []


class ExamStats(BaseModel):
    exam_id: str
    total_questions: int
    total_students: int
    average_score: float            # mean raw score
    score_std_dev: float            # standard deviation of scores
    cronbach_alpha: float           # internal consistency (0–1)
    reliability_label: str          # "Excellent", "Good", "Acceptable", "Poor", "Unacceptable"
    difficulty_distribution: Dict[str, int]   # {"Easy": 5, "Moderate": 12, "Hard": 3}
    flagged_question_count: int
    question_stats: List[QuestionStat]
