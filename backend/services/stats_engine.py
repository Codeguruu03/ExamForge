"""
Statistical Analysis Engine — Phase 3 Core
Implements Classical Test Theory (CTT) metrics:

  1. Difficulty Index (p-value)
     p = number_correct / total_students
     Range: 0 (impossible) → 1 (trivial). Ideal: 0.30–0.70.

  2. Discrimination Index (D-value)
     D = (correct_in_top27%) / top_n  −  (correct_in_bottom27%) / bottom_n
     Range: -1 → +1. Ideal: ≥ 0.30.

  3. Distractor Efficiency
     A non-correct option is "effective" if ≥ 5% of students chose it.
     Ineffective distractors → question may be too obvious.

  4. Cronbach's Alpha
     α = (k/(k-1)) × (1 − Σσᵢ² / σ²_total)
     Measures internal consistency (how well all items measure the same construct).

Input format (student_responses):
  A list of dicts, one per student:
  [
    {"student_id": "S01", "responses": {"1": "C", "2": "A", "3": "B"}},
    ...
  ]
  where keys are question IDs (str) and values are chosen option labels.

correct_answers:
  Dict mapping question_id (str) → correct option label (str):
  {"1": "C", "2": "B", ...}
"""

import numpy as np
from typing import List, Dict, Tuple
from backend.core.stat_models import (
    QuestionStat, DistractorStat, ExamStats
)
from backend.core.models import Exam


# ─── Label helpers ────────────────────────────────────────────────────────────

def _difficulty_label(p: float) -> str:
    if p >= 0.80:
        return "Easy"
    elif p >= 0.40:
        return "Moderate"
    else:
        return "Hard"


def _discrimination_label(d: float) -> str:
    if d >= 0.40:
        return "Excellent"
    elif d >= 0.30:
        return "Good"
    elif d >= 0.20:
        return "Fair"
    elif d >= 0.10:
        return "Poor"
    else:
        return "Remove"          # negative or near-zero — item should be reviewed


def _reliability_label(alpha: float) -> str:
    if alpha >= 0.90:
        return "Excellent"
    elif alpha >= 0.80:
        return "Good"
    elif alpha >= 0.70:
        return "Acceptable"
    elif alpha >= 0.60:
        return "Questionable"
    elif alpha >= 0.50:
        return "Poor"
    else:
        return "Unacceptable"


# ─── Core Engine ──────────────────────────────────────────────────────────────

class StatisticalEngine:

    @staticmethod
    def analyze(
        exam: Exam,
        student_responses: List[Dict],
        correct_answers: Dict[str, str],
    ) -> ExamStats:
        """
        Full CTT analysis pipeline.

        Parameters
        ----------
        exam              : Normalized Exam object (from Phase 2)
        student_responses : List of {"student_id": str, "responses": {q_id: chosen_label}}
        correct_answers   : {str(q_id): correct_label}

        Returns
        -------
        ExamStats object with all computed metrics
        """
        n_students = len(student_responses)
        if n_students < 2:
            raise ValueError("At least 2 student responses required for statistical analysis.")

        q_ids = [str(q.id) for q in exam.questions]

        # ── Build score matrix  (n_students × n_questions, 1=correct 0=wrong) ──
        score_matrix = StatisticalEngine._build_score_matrix(
            student_responses, correct_answers, q_ids
        )

        # Raw scores per student  (sum across questions)
        total_scores = score_matrix.sum(axis=1)          # shape (n_students,)

        # ── Sort students by total score for discrimination calc ──────────────
        sorted_idx = np.argsort(total_scores)
        cutoff = max(1, int(np.ceil(0.27 * n_students)))
        bottom_idx = sorted_idx[:cutoff]
        top_idx    = sorted_idx[-cutoff:]

        # ── Per-question analysis ─────────────────────────────────────────────
        question_stats: List[QuestionStat] = []
        diff_distribution = {"Easy": 0, "Moderate": 0, "Hard": 0}
        flagged_count = 0

        for i, q in enumerate(exam.questions):
            q_id = str(q.id)
            col = score_matrix[:, i]

            # 1. Difficulty Index
            p = float(col.mean())
            d_label = _difficulty_label(p)
            diff_distribution[d_label] += 1

            # 2. Discrimination Index
            top_correct    = float(col[top_idx].mean())
            bottom_correct = float(col[bottom_idx].mean())
            disc = round(top_correct - bottom_correct, 4)
            disc_label = _discrimination_label(disc)

            # 3. Distractor stats
            all_responses_for_q = [
                sr["responses"].get(q_id, "").upper()
                for sr in student_responses
            ]
            distractors = StatisticalEngine._distractor_stats(
                responses=all_responses_for_q,
                options=q.options,
                correct_label=correct_answers.get(q_id, "").upper(),
                n_students=n_students,
            )

            # 4. Flag logic
            flag_reasons = []
            if p < 0.20:
                flag_reasons.append("Extremely difficult (p < 0.20)")
            if p > 0.90:
                flag_reasons.append("Trivially easy (p > 0.90)")
            if disc < 0.10:
                flag_reasons.append(f"Poor discrimination (D={disc:.2f})")
            if disc < 0:
                flag_reasons.append("Negative discrimination — review item immediately")
            ineffective = [d for d in distractors if not d.is_correct and not d.is_effective]
            if len(ineffective) >= 2:
                flag_reasons.append(
                    f"{len(ineffective)} ineffective distractors (chosen by < 5%)"
                )

            is_flagged = bool(flag_reasons)
            if is_flagged:
                flagged_count += 1

            question_stats.append(QuestionStat(
                question_id=q.id,
                question_text=q.text,
                difficulty_index=round(p, 4),
                difficulty_label=d_label,
                discrimination_index=disc,
                discrimination_label=disc_label,
                distractors=distractors,
                is_flagged=is_flagged,
                flag_reasons=flag_reasons,
            ))

        # ── Cronbach's Alpha ──────────────────────────────────────────────────
        alpha = StatisticalEngine._cronbach_alpha(score_matrix)

        return ExamStats(
            exam_id=exam.exam_id,
            total_questions=exam.total_questions,
            total_students=n_students,
            average_score=round(float(total_scores.mean()), 2),
            score_std_dev=round(float(total_scores.std(ddof=1)), 2),
            cronbach_alpha=round(alpha, 4),
            reliability_label=_reliability_label(alpha),
            difficulty_distribution=diff_distribution,
            flagged_question_count=flagged_count,
            question_stats=question_stats,
        )

    # ─── Score Matrix ─────────────────────────────────────────────────────────

    @staticmethod
    def _build_score_matrix(
        student_responses: List[Dict],
        correct_answers: Dict[str, str],
        q_ids: List[str],
    ) -> np.ndarray:
        """
        Returns a (n_students × n_questions) binary numpy array.
        1 = student answered correctly, 0 = wrong or missing.
        """
        n = len(student_responses)
        k = len(q_ids)
        matrix = np.zeros((n, k), dtype=np.float64)

        for i, sr in enumerate(student_responses):
            responses = sr.get("responses", {})
            for j, q_id in enumerate(q_ids):
                student_ans = responses.get(q_id, "").strip().upper()
                correct_ans = correct_answers.get(q_id, "").strip().upper()
                if student_ans and correct_ans and student_ans == correct_ans:
                    matrix[i, j] = 1.0

        return matrix

    # ─── Distractor Efficiency ────────────────────────────────────────────────

    @staticmethod
    def _distractor_stats(
        responses: List[str],
        options,                         # List[Option] from Pydantic model
        correct_label: str,
        n_students: int,
    ) -> List[DistractorStat]:
        # Count how many chose each label
        counts: Dict[str, int] = {}
        for r in responses:
            if r:
                counts[r] = counts.get(r, 0) + 1

        stats = []
        for opt in options:
            lbl = opt.label.upper()
            chosen = counts.get(lbl, 0)
            pct = round(chosen / n_students * 100, 1) if n_students > 0 else 0.0
            is_correct = (lbl == correct_label)
            # A distractor is considered "effective" if ≥5% of students chose it
            is_effective = is_correct or pct >= 5.0

            stats.append(DistractorStat(
                label=lbl,
                text=opt.text,
                chosen_count=chosen,
                chosen_pct=pct,
                is_correct=is_correct,
                is_effective=is_effective,
            ))

        return stats

    # ─── Cronbach's Alpha ─────────────────────────────────────────────────────

    @staticmethod
    def _cronbach_alpha(score_matrix: np.ndarray) -> float:
        """
        Computes Cronbach's Alpha using the covariance formula.
        α = (k / (k-1)) × (1 − (Σ item_variances) / total_variance)

        Requires at least 2 items and 2 students.
        Returns 0.0 if computation is not possible.
        """
        n, k = score_matrix.shape
        if k < 2 or n < 2:
            return 0.0

        item_variances = score_matrix.var(axis=0, ddof=1)
        total_scores   = score_matrix.sum(axis=1)
        total_variance = total_scores.var(ddof=1)

        if total_variance == 0:
            return 0.0

        alpha = (k / (k - 1)) * (1 - item_variances.sum() / total_variance)
        # Clamp to [-1, 1] — negative alpha indicates fundamental structural issue
        return float(np.clip(alpha, -1.0, 1.0))
