"""
CSV Student Response Parser — Phase 3 supplement

Accepts two CSV formats:

Format A (wide — one row per student, columns = question IDs):
  student_id, 1, 2, 3, 4, ...
  S01,        C, A, B, D, ...

Format B (long — one row per answer):
  student_id, question_id, answer
  S01,        1,           C
  S01,        2,           A

Auto-detects format from the column headers.
Returns: List[{student_id, responses: {q_id: answer}}]
"""

import csv
import io
from typing import List, Dict


def parse_response_csv(content: bytes) -> List[Dict]:
    """
    Parse CSV bytes → list of student response dicts.
    Raises ValueError with a descriptive message on bad input.
    """
    try:
        text = content.decode("utf-8-sig")   # handle BOM from Excel exports
    except Exception:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    headers = [h.strip().lower() for h in (reader.fieldnames or [])]

    if not headers:
        raise ValueError("CSV has no headers. Expected either wide or long format.")

    # ── Detect format ─────────────────────────────────────────────────────────
    if "question_id" in headers and "answer" in headers:
        return _parse_long_format(reader, headers)
    elif "student_id" in headers or headers[0] in ("id", "student"):
        return _parse_wide_format(reader, headers)
    else:
        raise ValueError(
            "Cannot detect CSV format. Expected columns:\n"
            "  Wide: student_id, 1, 2, 3 ...\n"
            "  Long: student_id, question_id, answer"
        )


def _parse_wide_format(reader, headers: List[str]) -> List[Dict]:
    """
    Wide format: each non-student_id column is a question ID.
    """
    id_col = next((h for h in headers if h in ("student_id", "id", "student")), headers[0])
    q_cols = [h for h in headers if h != id_col]

    if not q_cols:
        raise ValueError("Wide CSV has no question columns after student_id.")

    results = []
    for row in reader:
        sid = str(row.get(id_col, "")).strip()
        if not sid:
            continue
        responses = {}
        for q in q_cols:
            ans = str(row.get(q, "")).strip().upper()
            if ans:
                responses[q.strip()] = ans
        results.append({"student_id": sid, "responses": responses})

    if not results:
        raise ValueError("CSV parsed but no student rows found.")

    return results


def _parse_long_format(reader, headers: List[str]) -> List[Dict]:
    """
    Long format: student_id, question_id, answer columns.
    """
    id_key  = next(h for h in headers if h == "student_id")
    qid_key = next(h for h in headers if h == "question_id")
    ans_key = next(h for h in headers if h == "answer")

    student_map: Dict[str, Dict] = {}
    for row in reader:
        sid = str(row.get(id_key, "")).strip()
        qid = str(row.get(qid_key, "")).strip()
        ans = str(row.get(ans_key, "")).strip().upper()
        if sid and qid and ans:
            if sid not in student_map:
                student_map[sid] = {}
            student_map[sid][qid] = ans

    results = [
        {"student_id": sid, "responses": resp}
        for sid, resp in student_map.items()
    ]

    if not results:
        raise ValueError("Long CSV parsed but no valid rows found.")

    return results
