"""
Pydantic data models for the Exam Reliability Analyzer.
These define the canonical structure for all data flowing through the system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class Option(BaseModel):
    label: str          # e.g., "A", "B", "C", "D"
    text: str           # e.g., "Paris"


class Question(BaseModel):
    id: int
    text: str
    options: List[Option] = []
    correct_option: Optional[str] = None   # label of the correct option, e.g. "C"
    subject_tag: Optional[str] = None
    # Quality metrics — populated later by the Statistical Engine
    difficulty_index: Optional[float] = None
    discrimination_index: Optional[float] = None
    is_flagged: Optional[bool] = False
    flag_reason: Optional[str] = None


class Exam(BaseModel):
    exam_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = "Untitled Exam"
    source_file: Optional[str] = None
    total_questions: int = 0
    questions: List[Question] = []


class NormalizationResult(BaseModel):
    exam: Exam
    warnings: List[str] = []   # e.g., "Question 3 has no options detected"
    raw_text_preview: Optional[str] = None
