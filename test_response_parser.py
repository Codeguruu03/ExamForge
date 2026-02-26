"""
Smoke test for CSV response parser — Phase 3
Run: python test_response_parser.py
"""
import sys
sys.path.insert(0, ".")

from backend.services.response_parser import parse_response_csv

# ── Test 1: Wide format ───────────────────────────────────────────────────────
wide_csv = b"""student_id,1,2,3,4
S01,C,A,B,D
S02,C,B,A,C
S03,A,A,B,D
S04,C,A,A,D
S05,B,C,B,C
"""

print("=== Wide Format ===")
rows = parse_response_csv(wide_csv)
for r in rows:
    print(f"  {r['student_id']}: {r['responses']}")
assert len(rows) == 5
assert rows[0]['responses']['1'] == 'C'
assert rows[0]['responses']['4'] == 'D'
print("  OK Wide format\n")

# ── Test 2: Long format ───────────────────────────────────────────────────────
long_csv = b"""student_id,question_id,answer
S01,1,C
S01,2,A
S01,3,B
S02,1,C
S02,2,B
S02,3,A
"""

print("=== Long Format ===")
rows = parse_response_csv(long_csv)
for r in rows:
    print(f"  {r['student_id']}: {r['responses']}")
assert len(rows) == 2
assert rows[0]['responses']['1'] == 'C'
print("  OK Long format\n")

# ── Test 3: Excel BOM ─────────────────────────────────────────────────────────
bom_csv = b'\xef\xbb\xbf' + b"student_id,1,2\nS01,A,B\nS02,C,D\n"
rows = parse_response_csv(bom_csv)
assert len(rows) == 2
print("  OK Excel BOM handled\n")

print("All response parser tests passed OK")
