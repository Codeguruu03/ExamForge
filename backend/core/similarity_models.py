"""
Pydantic models for the Similarity & Redundancy Detection Engine (Phase 4).
"""
from pydantic import BaseModel
from typing import List, Literal


class SimilarPair(BaseModel):
    question_id_1: int
    question_text_1: str
    question_id_2: int
    question_text_2: str
    similarity_score: float         # 0.0 → 1.0
    similarity_type: Literal["duplicate", "near_duplicate"]


class SimilarityCluster(BaseModel):
    cluster_id: int
    question_ids: List[int]
    question_texts: List[str]
    similarity_type: Literal["duplicate", "near_duplicate"]
    average_similarity: float


class SimilarityReport(BaseModel):
    total_questions: int
    duplicate_pairs: List[SimilarPair]          # ≥ 0.95 similarity
    near_duplicate_pairs: List[SimilarPair]     # 0.60 – 0.94 similarity
    clusters: List[SimilarityCluster]
    unique_question_count: int                  # questions in no cluster
