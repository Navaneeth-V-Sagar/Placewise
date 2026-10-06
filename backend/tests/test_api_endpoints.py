import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.database import Database
from app.schemas import SkillItem, Question, Evaluation

client = TestClient(app)

@pytest.fixture
def test_db(tmp_path):
    db_file = str(tmp_path / "test_placewise.db")
    test_database = Database(db_path=db_file)
    return test_database


def test_database_crud_operations(test_db):
    # 1. Create candidate
    candidate_id = test_db.create_candidate(
        name="Alice Smith",
        target_role="AI Engineer",
        resume_text="Experienced in Python, PyTorch, and Docker.",
        projects=["Computer Vision Pipeline"]
    )
    assert candidate_id > 0

    # 2. Get candidate
    cand = test_db.get_candidate(candidate_id)
    assert cand is not None
    assert cand["name"] == "Alice Smith"
    assert cand["target_role"] == "AI Engineer"
    assert "Computer Vision Pipeline" in cand["projects"]

    # 3. Create job
    job_id = test_db.create_job(
        candidate_id=candidate_id,
        target_role="AI Engineer",
        description="Looking for Python, PyTorch, and SQL skills.",
        required_skills=["Python", "PyTorch", "SQL"],
        preferred_skills=["Docker"]
    )
    assert job_id > 0

    # 4. Save skills
    skills = [
        SkillItem(skill_name="Python", score=80, required=True, preferred=False, source="resume", matched=True, status="strong"),
        SkillItem(skill_name="SQL", score=0, required=True, preferred=False, source="job_required", matched=False, status="gap"),
        SkillItem(skill_name="Docker", score=72, required=False, preferred=True, source="resume", matched=True, status="strong")
    ]
    test_db.save_skills(candidate_id, skills)

    loaded_skills = test_db.get_candidate_skills(candidate_id)
    assert len(loaded_skills) == 3
    sql_skill = next(s for s in loaded_skills if s.skill_name == "SQL")
    assert sql_skill.score == 0

    # 5. Update skill score
    test_db.update_skill_score(candidate_id, "SQL", 51)
    updated_skills = test_db.get_candidate_skills(candidate_id)
    updated_sql = next(s for s in updated_skills if s.skill_name == "SQL")
    assert updated_sql.score == 51

    # 6. Save question & attempt
    q = Question(skill="SQL", topic="LEFT JOIN", difficulty="Intermediate", question="Explain LEFT JOIN.")
    q_id = test_db.save_question(candidate_id, q)
    assert q_id > 0

    ev = Evaluation(
        score=70,
        correctness="Partially Correct",
        missing_concepts=["NULL handling"],
        feedback="Good attempt.",
        recommended_next_topic="NULL handling"
    )
    attempt_id = test_db.save_attempt(
        question_id=q_id,
        candidate_id=candidate_id,
        skill="SQL",
        topic="LEFT JOIN",
        difficulty="Intermediate",
        question="Explain LEFT JOIN.",
        answer="A join that returns all left rows.",
        evaluation=ev
    )
    assert attempt_id > 0

    attempts = test_db.get_candidate_attempts(candidate_id)
    assert len(attempts) == 1
    assert attempts[0].score == 70


def test_api_candidate_profile_not_found():
    response = client.get("/api/candidate/999999")
    assert response.status_code == 404
