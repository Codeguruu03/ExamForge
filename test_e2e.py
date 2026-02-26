"""
End-to-End Integration Test for ExamForge
Tests the core API endpoints:
1. upload (simulated normalization output)
2. similarity (duplicate detection)
3. responses (CTT statistics)
"""
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, ".")
from backend.main import app
from backend.core.models import Exam, Question, Option

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    print("✓ Health check OK")

def test_similarity_and_responses():
    # 1. Create a mock Exam JSON
    exam_data = {
        "exam_id": "test-123",
        "title": "Mock Exam",
        "source_file": "mock.pdf",
        "total_questions": 4,
        "questions": [
            {
                "id": 1,
                "text": "What is the capital of France?",
                "options": [
                    {"label": "A", "text": "London"},
                    {"label": "B", "text": "Berlin"},
                    {"label": "C", "text": "Paris"},
                    {"label": "D", "text": "Madrid"}
                ],
                "correct_option": "C"
            },
            {
                "id": 2,
                "text": "Who wrote Hamlet?",
                "options": [
                    {"label": "A", "text": "Shakespeare"},
                    {"label": "B", "text": "Dickens"},
                    {"label": "C", "text": "Austen"},
                    {"label": "D", "text": "Twain"}
                ],
                "correct_option": "A"
            },
            {
                "id": 3,
                "text": "What is the capital of France?", # Exact duplicate of Q1
                "options": [
                    {"label": "A", "text": "Paris"},
                    {"label": "B", "text": "Rome"},
                    {"label": "C", "text": "Berlin"},
                    {"label": "D", "text": "Madrid"}
                ],
                "correct_option": "A"
            },
            {
                "id": 4,
                "text": "What is 2 + 2?",
                "options": [
                    {"label": "A", "text": "3"},
                    {"label": "B", "text": "4"},
                    {"label": "C", "text": "5"},
                    {"label": "D", "text": "6"}
                ],
                "correct_option": "B"
            }
        ]
    }

    # 2. Test Similarity Endpoint
    print("Testing /api/similarity/...")
    sim_resp = client.post("/api/similarity/", json={"exam": exam_data})
    assert sim_resp.status_code == 200, f"Similarity failed: {sim_resp.text}"
    sim_data = sim_resp.json()
    assert "clusters" in sim_data
    assert "duplicate_pairs" in sim_data
    # Q1 and Q3 should be identified as duplicate or near-duplicate
    pairs = sim_data["duplicate_pairs"] + sim_data["near_duplicate_pairs"]
    assert len(pairs) > 0
    print(f"✓ Similarity OK (Found {len(pairs)} similar pair(s))")

    # 3. Test Responses / CTT Analysis Endpoint
    print("Testing /api/responses/upload...")
    csv_content = b"student_id,1,2,3,4\nS1,C,A,A,B\nS2,C,B,A,B\nS3,A,A,A,C\nS4,C,A,B,B\nS5,B,C,A,B\n"
    correct_answers = {"1": "C", "2": "A", "3": "A", "4": "B"}
    
    files = {"file": ("students.csv", csv_content, "text/csv")}
    data = {
        "exam_json": json.dumps(exam_data),
        "correct_answers_json": json.dumps(correct_answers)
    }

    resp = client.post("/api/responses/upload", data=data, files=files)
    assert resp.status_code == 200, f"Responses failed: {resp.text}"
    stats_data = resp.json()
    
    assert "cronbach_alpha" in stats_data
    assert "question_stats" in stats_data
    assert len(stats_data["question_stats"]) == 4
    print(f"✓ CTT Responses OK (Cronbach Alpha: {stats_data['cronbach_alpha']:.3f})")

if __name__ == "__main__":
    try:
        test_health()
        test_similarity_and_responses()
        print("\nAll E2E Tests Passed! 🚀")
    except Exception as e:
        import traceback
        print("\n\u274c E2E Test Failed")
        traceback.print_exc()
        sys.exit(1)
