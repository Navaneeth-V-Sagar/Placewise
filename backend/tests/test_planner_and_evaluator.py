import pytest
from datetime import datetime
from app.services.planner import adaptive_planner, AdaptivePlanner
from app.services.evaluator import answer_evaluator, AnswerEvaluator
from app.schemas import (
    SkillItem,
    GapItem,
    QuestionAttemptItem,
    Question
)


def test_deterministic_score_update_formula():
    # 1. Example from Section 27: 42 -> answer 72 -> 51
    # 0.7 * 42 + 0.3 * 72 = 29.4 + 21.6 = 51.0
    updated = AnswerEvaluator.calculate_updated_score(previous_score=42, answer_score=72)
    assert updated == 51

    # 2. Perfect score on weak baseline: 0 -> 100 -> 30
    assert AnswerEvaluator.calculate_updated_score(previous_score=0, answer_score=100) == 30

    # 3. Dropping score on mistake: 80 -> 0 -> 56
    assert AnswerEvaluator.calculate_updated_score(previous_score=80, answer_score=0) == 56

    # 4. High mastery: 70 -> 100 -> 79
    assert AnswerEvaluator.calculate_updated_score(previous_score=70, answer_score=100) == 79


def test_planner_gap_prioritization():
    gaps = [
        GapItem(skill_name="SQL", score=42, importance="required", priority=2, reason="Weak baseline"),
        GapItem(skill_name="Docker", score=0, importance="preferred", priority=4, reason="Missing")
    ]
    skills = [
        SkillItem(skill_name="SQL", score=42, required=True, preferred=False, source="job_required", matched=True, status="gap"),
        SkillItem(skill_name="Python", score=80, required=True, preferred=False, source="resume", matched=True, status="strong")
    ]

    rec = adaptive_planner.recommend_next_step(gaps=gaps, skills=skills, recent_attempts=[])
    assert "SQL" in rec.current_weakness
    assert "LEFT JOIN" in rec.recommended_topic or "SQL" in rec.recommended_topic
    assert rec.difficulty in ["Beginner", "Intermediate"]


def test_planner_remediation_after_mistake():
    gaps = [
        GapItem(skill_name="SQL", score=51, importance="required", priority=2, reason="Needs practice")
    ]
    skills = [
        SkillItem(skill_name="SQL", score=51, required=True, preferred=False, source="job_required", matched=True, status="moderate")
    ]
    recent_attempts = [
        QuestionAttemptItem(
            id=1,
            skill="SQL",
            topic="LEFT JOIN & NULL Handling",
            difficulty="Intermediate",
            question="Explain how LEFT JOIN handles non-matching rows.",
            answer="It combines all rows.",
            score=35,
            correctness="Incorrect",
            missing_concepts=["NULL values for non-matching right table rows", "WHERE clause filtering on NULLs"],
            feedback="You missed explaining how missing rows are filled with NULL values.",
            recommended_next_topic="LEFT JOIN NULL Handling",
            created_at=datetime.now()
        )
    ]

    rec = adaptive_planner.recommend_next_step(gaps=gaps, skills=skills, recent_attempts=recent_attempts)
    assert "SQL" in rec.current_weakness
    assert "LEFT JOIN" in rec.recommended_topic
    assert "NULL" in rec.reason or "struggled" in rec.reason


@pytest.mark.anyio
async def test_evaluator_empty_answer():
    q = Question(
        skill="SQL",
        topic="LEFT JOIN",
        difficulty="Intermediate",
        question="What happens when a LEFT JOIN finds no match in the right table?"
    )
    eval_res, new_score = await answer_evaluator.evaluate_answer(
        question=q,
        candidate_answer="",
        previous_score=50
    )
    assert eval_res.score == 0
    assert eval_res.correctness == "Incorrect"
    assert new_score == 35  # 0.7 * 50 + 0 = 35
