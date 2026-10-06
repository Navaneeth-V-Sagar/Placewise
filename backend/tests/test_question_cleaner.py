import pytest
from app.services.planner import adaptive_planner
from app.services.question_generator import question_generator, QuestionGenerator
from app.schemas import GapItem, SkillItem, PlannerRecommendation

def test_clean_question_text_preamble_removal():
    raw_with_preamble = "Okay, let's tackle this. The user wants an interview question for an AI Engineer focusing on REST APIs.\n\nExplain how idempotency is maintained in RESTful APIs when using PUT vs POST requests."
    cleaned = QuestionGenerator.clean_question_text(raw_with_preamble, "REST APIs", "Idempotency")
    assert "Okay, let's tackle this" not in cleaned
    assert "The user wants" not in cleaned
    assert "Explain how idempotency is maintained" in cleaned


def test_clean_question_text_embedded_quote_extraction():
    raw_with_thoughts = 'Wait, the difficulty is easy, so the question shouldn\'t be too complex. Maybe a simpler question. Like: "What is a REST API and why is it important in web applications?"'
    cleaned = QuestionGenerator.clean_question_text(raw_with_thoughts, "REST APIs", "REST API Fundamentals")
    assert cleaned == "What is a REST API and why is it important in web applications?"


@pytest.mark.anyio
async def test_question_generator_deterministic_target():
    rec = PlannerRecommendation(
        current_weakness="REST APIs (Score: 0%)",
        recommended_topic="REST API Fundamentals",
        difficulty="Easy",
        reason="Required job requirement with critical gap.",
        next_action="Start with conceptual question on REST API Fundamentals."
    )
    
    q = await question_generator.generate_question(
        target_role="AI/ML Software Engineer Intern",
        recommendation=rec
    )
    
    # Must strictly be REST APIs and REST API Fundamentals, NOT "Technical" or "Applied Concepts"
    assert q.skill == "REST APIs"
    assert q.topic == "REST API Fundamentals"
    assert q.difficulty == "Easy"
    assert "Okay, let's tackle this" not in q.question
    assert "The user wants" not in q.question
    assert "Wait," not in q.question
    assert len(q.question) > 15
    print(f"\n[Generated Question] Skill: {q.skill} | Topic: {q.topic} | Diff: {q.difficulty}")
    print(f"[Question Text] {q.question}")
