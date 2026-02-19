"""
Normalization Engine — Phase 2 Core.

Converts cleaned raw text into a structured Exam object using
multi-pattern regex matching for:
  - Question detection (numbered, Q-prefixed, etc.)
  - Option detection ((a)/(A)/A./i) formats)
  - Answer key detection (inline or trailing)
"""
import re
from typing import List, Tuple, Optional
from backend.core.models import Exam, Question, Option, NormalizationResult
from backend.services.cleaner import clean_text


# ─── Regex Patterns ──────────────────────────────────────────────────────────

# Matches question starters like:
#   "1.", "1)", "Q1.", "Q.1", "Q1)", "Question 1.", "1 ."
_QUESTION_START = re.compile(
    r"^(?:Q(?:uestion)?[\s.]*)?"    # optional Q / Question prefix
    r"(\d{1,3})"                    # question number (capture group 1)
    r"[\s.)\-:]+"                   # separator
    r"(.+)",                        # question text (capture group 2)
    re.IGNORECASE
)

# Matches option lines like:
#   "(a) Paris", "A. Paris", "A) Paris", "(A) Paris", "a. Paris", "i) Paris"
_OPTION_LINE = re.compile(
    r"^\(?([A-Ea-e]|[ivxIVX]{1,4})\)?[\s.)\-:]+(.+)"
)

# Matches answer key lines like:
#   "Answer: C", "Ans: (b)", "Correct Answer: A", "Key: D"
_ANSWER_LINE = re.compile(
    r"^(?:answer|ans|correct\s+answer|key)[\s:.\-]+\(?([A-Ea-e])\)?",
    re.IGNORECASE
)


# ─── Main Normalizer ─────────────────────────────────────────────────────────

def normalize(raw_text: str, source_file: str = None) -> NormalizationResult:
    """
    Full pipeline: clean → segment → parse → validate → return NormalizationResult.
    """
    cleaned = clean_text(raw_text)
    questions, warnings = _parse_questions(cleaned)

    exam = Exam(
        source_file=source_file,
        total_questions=len(questions),
        questions=questions,
    )

    return NormalizationResult(
        exam=exam,
        warnings=warnings,
        raw_text_preview=cleaned[:500] if cleaned else None,
    )


def _parse_questions(text: str) -> Tuple[List[Question], List[str]]:
    """
    Segments text into question blocks and parses each one.
    """
    lines = text.splitlines()
    questions: List[Question] = []
    warnings: List[str] = []

    current_q_num: Optional[int] = None
    current_q_text: str = ""
    current_options: List[Option] = []
    current_answer: Optional[str] = None
    continuation_lines: List[str] = []

    def _flush():
        """Commit the current question buffer to the questions list."""
        nonlocal current_q_num, current_q_text, current_options, current_answer, continuation_lines

        if current_q_num is None:
            return

        full_text = current_q_text
        if continuation_lines:
            full_text += " " + " ".join(continuation_lines)
        full_text = full_text.strip()

        q = Question(
            id=current_q_num,
            text=full_text,
            options=current_options[:],
            correct_option=current_answer,
        )

        if not current_options:
            warnings.append(f"Q{current_q_num}: No options detected.")
        if len(current_options) < 2:
            q.is_flagged = True
            q.flag_reason = "Fewer than 2 options found."

        questions.append(q)

        # Reset buffer
        current_q_num = None
        current_q_text = ""
        current_options = []
        current_answer = None
        continuation_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. Check for answer key line
        ans_match = _ANSWER_LINE.match(line)
        if ans_match and current_q_num is not None:
            current_answer = ans_match.group(1).upper()
            continue

        # 2. Check for option line
        opt_match = _OPTION_LINE.match(line)
        if opt_match and current_q_num is not None:
            label = opt_match.group(1).upper()
            text = opt_match.group(2).strip()
            current_options.append(Option(label=label, text=text))
            continue

        # 3. Check for new question
        q_match = _QUESTION_START.match(line)
        if q_match:
            _flush()  # save previous question
            current_q_num = int(q_match.group(1))
            current_q_text = q_match.group(2).strip()
            continuation_lines = []
            continue

        # 4. Continuation of current question text (before any options)
        if current_q_num is not None and not current_options:
            continuation_lines.append(line)

    # Flush the last question
    _flush()

    return questions, warnings
