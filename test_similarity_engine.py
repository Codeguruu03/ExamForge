"""
Smoke test for Phase 4 — Similarity & Redundancy Detection Engine.
Run: python test_similarity_engine.py
"""
import sys
sys.path.insert(0, ".")

from backend.core.models import Exam, Question, Option
from backend.services.similarity_engine import SimilarityEngine

exam = Exam(
    exam_id="sim-test-001",
    title="Similarity Test Paper",
    total_questions=6,
    questions=[
        Question(id=1, text="What is the capital of France?",
                 options=[Option(label="A", text="London"), Option(label="B", text="Paris")]),
        Question(id=2, text="What is France's capital city?",   # near-duplicate of Q1
                 options=[Option(label="A", text="Berlin"), Option(label="B", text="Paris")]),
        Question(id=3, text="What is the capital of France?",   # exact duplicate of Q1
                 options=[Option(label="A", text="London"), Option(label="B", text="Paris")]),
        Question(id=4, text="Who wrote Romeo and Juliet?",
                 options=[Option(label="A", text="Shakespeare"), Option(label="B", text="Dickens")]),
        Question(id=5, text="Who authored Romeo and Juliet?",   # near-duplicate of Q4
                 options=[Option(label="A", text="Marlowe"), Option(label="B", text="Shakespeare")]),
        Question(id=6, text="Calculate the speed of light in vacuum.",  # unique
                 options=[Option(label="A", text="3e8 m/s"), Option(label="B", text="3e6 m/s")]),
    ]
)

report = SimilarityEngine.analyze(exam.questions)

print(f"\n{'='*60}")
print(f"  SIMILARITY REPORT")
print(f"{'='*60}")
print(f"  Total Questions   : {report.total_questions}")
print(f"  Unique Questions  : {report.unique_question_count}")
print(f"  Duplicate Pairs   : {len(report.duplicate_pairs)}")
print(f"  Near-Dup Pairs    : {len(report.near_duplicate_pairs)}")
print(f"  Clusters Found    : {len(report.clusters)}")

if report.duplicate_pairs:
    print(f"\n  🔴 DUPLICATES:")
    for p in report.duplicate_pairs:
        print(f"    Q{p.question_id_1} ↔ Q{p.question_id_2}  [{p.similarity_score:.2%}]")
        print(f"      '{p.question_text_1}'")
        print(f"      '{p.question_text_2}'")

if report.near_duplicate_pairs:
    print(f"\n  🟡 NEAR-DUPLICATES:")
    for p in report.near_duplicate_pairs:
        print(f"    Q{p.question_id_1} ↔ Q{p.question_id_2}  [{p.similarity_score:.2%}]")
        print(f"      '{p.question_text_1}'")
        print(f"      '{p.question_text_2}'")

if report.clusters:
    print(f"\n  📦 CLUSTERS:")
    for c in report.clusters:
        print(f"    Cluster {c.cluster_id} [{c.similarity_type}  avg={c.average_similarity:.2%}]")
        for qid, qt in zip(c.question_ids, c.question_texts):
            print(f"      Q{qid}: {qt}")

print(f"\n{'='*60}\n")
