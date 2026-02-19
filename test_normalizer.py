"""
Quick smoke test for the normalization pipeline.
Run: python test_normalizer.py
"""
import sys
sys.path.insert(0, ".")

from backend.services.normalizer import normalize

SAMPLE_TEXT = """
Page 1

1. What is the capital of France?
(A) London
(B) Berlin
(C) Paris
(D) Madrid
Answer: C

2. Which planet is closest to the Sun?
A. Earth
B. Venus
C. Mercury
D. Mars

3. The speed of light is approximately:
(a) 3 x 10^8 m/s
(b) 3 x 10^6 m/s
(c) 3 x 10^10 m/s
(d) 3 x 10^4 m/s
Ans: a

4. Who wrote Hamlet?
A) Charles Dickens
B) William Shakespeare
C) Leo Tolstoy
D) Mark Twain
"""

result = normalize(SAMPLE_TEXT, source_file="test_paper.pdf")

print(f"\n✅ Exam ID     : {result.exam.exam_id}")
print(f"✅ Total Qs   : {result.exam.total_questions}")
print(f"⚠️  Warnings   : {result.warnings}")
print()

for q in result.exam.questions:
    print(f"  Q{q.id}: {q.text}")
    for opt in q.options:
        marker = "✓" if opt.label == q.correct_option else " "
        print(f"    [{marker}] {opt.label}. {opt.text}")
    if q.is_flagged:
        print(f"    ⚑ FLAGGED: {q.flag_reason}")
    print()
