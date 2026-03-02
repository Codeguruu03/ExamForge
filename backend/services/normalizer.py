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

# Matches question starters:
# - With Q: "Q1", "Q.1", "Question 1:" (allows spaces after)
# - Without Q: "1.", "1)", "1-" (MUST have a punctuation mark AND space or eol to prevent matching "5.20m")
_QUESTION_START = re.compile(
    r"^(?:Q(?:uestion)?\s*(\d{1,3})[\s.)\-:]*|(\d{1,3})[.)\-:]+(?=\s|$))\s*(.*)",
    re.IGNORECASE
)

# Matches option lines:
# - "(a)", "(A)", "a.", "A)", "i)"
# - MUST have a surrounding parenthesis or a trailing punctuation mark.
_OPTION_START = re.compile(
    r"^(?:\(([A-Ea-e]|[ivxIVX]{1,4})\)|([A-Ea-e]|[ivxIVX]{1,4})[.)\-:])\s*(.*)$"
)

# Matches answer key lines:
_ANSWER_LINE = re.compile(
    r"^(?:answer|ans|correct\s+answer|key)[\s:.\-]+\(?([A-Ea-e])\)?",
    re.IGNORECASE
)


# ─── Main Normalizer ─────────────────────────────────────────────────────────

def normalize(raw_text: str, source_file: str = None) -> NormalizationResult:
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
    lines = text.splitlines()
    questions: List[Question] = []
    warnings: List[str] = []

    current_q_num: Optional[int] = None
    current_q_text: List[str] = []
    current_options: List[Option] = []
    current_answer: Optional[str] = None
    
    # State tracking: "TEXT" or "OPTION"
    # If "OPTION", we append subsequent lines to the LAST option's text
    current_state = "ROOT" 

    def _flush():
        nonlocal current_q_num, current_q_text, current_options, current_answer
        
        # Don't save if there's no actual question text (e.g., random "1." from a grid)
        full_text = " ".join(current_q_text).strip()
        if current_q_num is None or not full_text:
            return

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

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. Check for answer key
        ans_match = _ANSWER_LINE.match(line)
        if ans_match and current_q_num is not None:
            current_answer = ans_match.group(1).upper()
            continue

        # 2. Check for new question
        q_match = _QUESTION_START.match(line)
        if q_match:
            _flush()  # save previous
            q_num_str = q_match.group(1) or q_match.group(2)
            current_q_num = int(q_num_str)
            remainder = q_match.group(3)
            current_q_text = [remainder.strip()] if remainder.strip() else []
            current_options = []
            current_answer = None
            current_state = "TEXT"
            continue

        # 3. Check for option line
        opt_match = _OPTION_START.match(line)
        # Avoid matching random standalone text as options unless we are currently inside a question
        if opt_match and current_q_num is not None:
            label = (opt_match.group(1) or opt_match.group(2)).upper()
            remainder = opt_match.group(3)
            current_options.append(Option(label=label, text=remainder.strip() if remainder else ""))
            current_state = "OPTION"
            continue

        # 4. Continuation line
        if current_q_num is not None:
            if current_state == "TEXT":
                current_q_text.append(line)
            elif current_state == "OPTION" and len(current_options) > 0:
                # Append to the last option's text
                last_opt = current_options[-1]
                last_opt.text = (last_opt.text + " " + line).strip()

    _flush()
    return questions, warnings
