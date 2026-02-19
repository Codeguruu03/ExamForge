"""
Smoke test for Phase 3 — Statistical Analysis Engine.
Run: python test_stats_engine.py
"""
import sys
sys.path.insert(0, ".")

from backend.core.models import Exam, Question, Option
from backend.services.stats_engine import StatisticalEngine

# ── Build a mock exam with 4 questions ──────────────────────────────────────
exam = Exam(
    exam_id="test-001",
    title="Mock Science Paper",
    total_questions=4,
    questions=[
        Question(id=1, text="What is the capital of France?",
                 options=[Option(label="A", text="London"),
                           Option(label="B", text="Berlin"),
                           Option(label="C", text="Paris"),
                           Option(label="D", text="Madrid")]),
        Question(id=2, text="Which planet is closest to the Sun?",
                 options=[Option(label="A", text="Earth"),
                           Option(label="B", text="Venus"),
                           Option(label="C", text="Mercury"),
                           Option(label="D", text="Mars")]),
        Question(id=3, text="Speed of light (m/s)?",
                 options=[Option(label="A", text="3e8"),
                           Option(label="B", text="3e6"),
                           Option(label="C", text="3e10"),
                           Option(label="D", text="3e4")]),
        Question(id=4, text="Who wrote Hamlet?",
                 options=[Option(label="A", text="Dickens"),
                           Option(label="B", text="Shakespeare"),
                           Option(label="C", text="Tolstoy"),
                           Option(label="D", text="Twain")]),
    ]
)

correct_answers = {"1": "C", "2": "C", "3": "A", "4": "B"}

# ── Mock 10 student responses ─────────────────────────────────────────────────
student_responses = [
    {"student_id": "S01", "responses": {"1": "C", "2": "C", "3": "A", "4": "B"}},  # 4/4
    {"student_id": "S02", "responses": {"1": "C", "2": "C", "3": "A", "4": "B"}},  # 4/4
    {"student_id": "S03", "responses": {"1": "C", "2": "C", "3": "B", "4": "B"}},  # 3/4
    {"student_id": "S04", "responses": {"1": "C", "2": "B", "3": "A", "4": "B"}},  # 3/4
    {"student_id": "S05", "responses": {"1": "A", "2": "C", "3": "A", "4": "B"}},  # 3/4
    {"student_id": "S06", "responses": {"1": "C", "2": "A", "3": "B", "4": "A"}},  # 1/4
    {"student_id": "S07", "responses": {"1": "B", "2": "A", "3": "D", "4": "C"}},  # 0/4
    {"student_id": "S08", "responses": {"1": "D", "2": "D", "3": "C", "4": "A"}},  # 0/4
    {"student_id": "S09", "responses": {"1": "C", "2": "B", "3": "A", "4": "A"}},  # 2/4
    {"student_id": "S10", "responses": {"1": "C", "2": "C", "3": "A", "4": "C"}},  # 3/4
]

# ── Run analysis ──────────────────────────────────────────────────────────────
stats = StatisticalEngine.analyze(exam, student_responses, correct_answers)

print(f"\n{'='*60}")
print(f"  EXAM: {stats.exam_id}")
print(f"{'='*60}")
print(f"  Students       : {stats.total_students}")
print(f"  Avg Score      : {stats.average_score} / {stats.total_questions}")
print(f"  Std Deviation  : {stats.score_std_dev}")
print(f"  Cronbach Alpha : {stats.cronbach_alpha}  → {stats.reliability_label}")
print(f"  Difficulty Dist: {stats.difficulty_distribution}")
print(f"  Flagged Qs     : {stats.flagged_question_count}")
print(f"\n  {'Q':<4} {'p-val':<8} {'Difficulty':<12} {'D-val':<8} {'Discrimination':<18} {'Flagged'}")
print(f"  {'-'*70}")
for q in stats.question_stats:
    flag = "⚑ " + ", ".join(q.flag_reasons) if q.is_flagged else ""
    print(f"  Q{q.question_id:<3} {q.difficulty_index:<8.3f} {q.difficulty_label:<12} "
          f"{q.discrimination_index:<8.3f} {q.discrimination_label:<18} {flag}")
print(f"\n{'='*60}\n")
