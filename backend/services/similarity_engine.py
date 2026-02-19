"""
Similarity & Redundancy Detection Engine — Phase 4

Uses TF-IDF vectorization + Cosine Similarity to detect:
  1. Exact duplicates            (similarity ≥ 0.95)
  2. Near-duplicates / paraphrases  (0.60 ≤ similarity < 0.95)
  3. Unique questions               (similarity < 0.60)

Algorithm:
  - Question texts are vectorized using TF-IDF (unigrams + bigrams)
  - Cosine similarity is computed as a full N×N matrix
  - Upper triangle is scanned to find pairs above threshold
  - Results are grouped into similarity clusters
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from backend.core.similarity_models import (
    SimilarPair, SimilarityCluster, SimilarityReport
)


# ─── Thresholds ───────────────────────────────────────────────────────────────
DUPLICATE_THRESHOLD    = 0.95   # treat as exact duplicate
NEAR_DUP_THRESHOLD     = 0.60   # treat as near-duplicate / paraphrase
DISTRACTOR_EFFICIENCY  = 5      # min % for a distractor to be "effective" (from Phase 3)


class SimilarityEngine:

    @staticmethod
    def analyze(questions: list) -> SimilarityReport:
        """
        Run TF-IDF + Cosine Similarity on all questions.

        Parameters
        ----------
        questions : List of Question objects (from Pydantic model)

        Returns
        -------
        SimilarityReport
        """
        texts = [q.text.strip() for q in questions]
        q_ids = [q.id for q in questions]
        n = len(texts)

        if n < 2:
            return SimilarityReport(
                total_questions=n,
                duplicate_pairs=[],
                near_duplicate_pairs=[],
                clusters=[],
                unique_question_count=n,
            )

        # ── TF-IDF vectorization (unigrams + bigrams) ─────────────────────────
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            min_df=1,
            sublinear_tf=True,      # log normalization reduces impact of frequent terms
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # ── Cosine similarity matrix (n × n) ─────────────────────────────────
        sim_matrix = cosine_similarity(tfidf_matrix)

        # ── Scan upper triangle for similar pairs ─────────────────────────────
        duplicate_pairs: List[SimilarPair] = []
        near_dup_pairs:  List[SimilarPair] = []

        for i in range(n):
            for j in range(i + 1, n):
                score = float(sim_matrix[i, j])
                if score >= DUPLICATE_THRESHOLD:
                    duplicate_pairs.append(SimilarPair(
                        question_id_1=q_ids[i],
                        question_text_1=texts[i],
                        question_id_2=q_ids[j],
                        question_text_2=texts[j],
                        similarity_score=round(score, 4),
                        similarity_type="duplicate",
                    ))
                elif score >= NEAR_DUP_THRESHOLD:
                    near_dup_pairs.append(SimilarPair(
                        question_id_1=q_ids[i],
                        question_text_1=texts[i],
                        question_id_2=q_ids[j],
                        question_text_2=texts[j],
                        similarity_score=round(score, 4),
                        similarity_type="near_duplicate",
                    ))

        # ── Build clusters (union-find grouping) ──────────────────────────────
        clusters = SimilarityEngine._build_clusters(
            duplicate_pairs + near_dup_pairs, q_ids, texts
        )

        # ── Questions not in any cluster are unique ───────────────────────────
        clustered_ids = {
            qid for c in clusters for qid in c.question_ids
        }
        unique_count = sum(1 for qid in q_ids if qid not in clustered_ids)

        return SimilarityReport(
            total_questions=n,
            duplicate_pairs=duplicate_pairs,
            near_duplicate_pairs=near_dup_pairs,
            clusters=clusters,
            unique_question_count=unique_count,
        )

    @staticmethod
    def _build_clusters(
        pairs: List[SimilarPair],
        q_ids: list,
        texts: list,
    ) -> List[SimilarityCluster]:
        """
        Simple union-find to group similar questions into clusters.
        Each cluster represents a group of questions that are similar to each other.
        """
        parent = {qid: qid for qid in q_ids}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            parent[find(x)] = find(y)

        for pair in pairs:
            union(pair.question_id_1, pair.question_id_2)

        # Group by root
        groups: dict = {}
        for qid in q_ids:
            root = find(qid)
            groups.setdefault(root, []).append(qid)

        clusters = []
        id_to_text = dict(zip(q_ids, texts))
        cluster_id = 1

        for root, members in groups.items():
            if len(members) < 2:
                continue   # singletons are not clusters
            # Determine the dominant type in this cluster
            member_set = set(members)
            cluster_pairs = [
                p for p in pairs
                if p.question_id_1 in member_set and p.question_id_2 in member_set
            ]
            has_duplicate = any(p.similarity_type == "duplicate" for p in cluster_pairs)
            cluster_type = "duplicate" if has_duplicate else "near_duplicate"

            avg_score = (
                sum(p.similarity_score for p in cluster_pairs) / len(cluster_pairs)
                if cluster_pairs else 0.0
            )

            clusters.append(SimilarityCluster(
                cluster_id=cluster_id,
                question_ids=members,
                question_texts=[id_to_text[m] for m in members],
                similarity_type=cluster_type,
                average_similarity=round(avg_score, 4),
            ))
            cluster_id += 1

        return clusters
