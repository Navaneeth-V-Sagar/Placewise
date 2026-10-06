from fastapi import APIRouter, HTTPException, status
import logging
from app.database import db
from app.services.planner import adaptive_planner
from app.services.question_generator import question_generator
from app.services.evaluator import answer_evaluator
from app.schemas import (
    Question,
    EvaluationRequest,
    EvaluationResponse,
    GapItem
)

router = APIRouter(tags=["Assessment"])
logger = logging.getLogger("placewise.api.assessment")


@router.get("/candidate/{candidate_id}/next-question")
async def get_next_adaptive_question(candidate_id: int):
    """
    Generates a targeted, adaptive interview question based on the candidate's
    current priority skill gap and previous attempt history.
    """
    candidate = db.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found."
        )

    skills = db.get_candidate_skills(candidate_id)
    attempts = db.get_candidate_attempts(candidate_id, limit=5)

    # Determine current gaps
    gaps = []
    for s in skills:
        if s.score < 70 and (s.required or s.preferred):
            priority = 1 if (s.required and s.score == 0) else (2 if s.required else 4)
            gaps.append(GapItem(
                skill_name=s.skill_name,
                score=s.score,
                importance="required" if s.required else "preferred",
                priority=priority,
                reason="Required/preferred role competency gap"
            ))
    gaps.sort(key=lambda g: (g.priority, g.score))

    # 1. Compute adaptive recommendation
    rec = adaptive_planner.recommend_next_step(
        gaps=gaps,
        skills=skills,
        recent_attempts=attempts
    )

    # 2. Extract previous mistake context if applicable
    previous_mistakes = None
    if attempts:
        last = attempts[0]
        if last.missing_concepts:
            previous_mistakes = f"Previous topic: {last.topic}. Missed concepts: {', '.join(last.missing_concepts)}"

    # 3. Generate targeted question using Qwen3
    try:
        generated_q = await question_generator.generate_question(
            target_role=candidate["target_role"],
            recommendation=rec,
            previous_mistakes=previous_mistakes
        )
    except Exception as e:
        logger.error(f"Question generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error generating adaptive question: {str(e)}"
        )

    # 4. Save question to database
    question_id = db.save_question(candidate_id=candidate_id, question=generated_q)

    return {
        "question_id": question_id,
        "candidate_id": candidate_id,
        "skill": generated_q.skill,
        "topic": generated_q.topic,
        "difficulty": generated_q.difficulty,
        "question": generated_q.question,
        "recommendation_context": rec
    }


@router.post("/candidate/{candidate_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_candidate_answer(candidate_id: int, req: EvaluationRequest):
    """
    Evaluates candidate's answer, deterministically updates the skill score in DB,
    and returns feedback along with the next adaptive recommendation.
    """
    candidate = db.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found."
        )

    # Fetch question
    q_data = db.get_question(req.question_id)
    if not q_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {req.question_id} not found."
        )

    question_obj = Question(
        skill=q_data["skill"],
        topic=q_data["topic"],
        difficulty=q_data["difficulty"],
        question=q_data["question"]
    )

    # Get previous skill score
    skills = db.get_candidate_skills(candidate_id)
    current_skill_item = next((s for s in skills if s.skill_name.lower() == question_obj.skill.lower()), None)
    previous_score = current_skill_item.score if current_skill_item else 0

    # Evaluate answer via LLM
    try:
        evaluation, new_score = await answer_evaluator.evaluate_answer(
            question=question_obj,
            candidate_answer=req.answer,
            previous_score=previous_score
        )
    except Exception as e:
        logger.error(f"Answer evaluation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error evaluating candidate answer: {str(e)}"
        )

    # Update skill score in DB
    db.update_skill_score(
        candidate_id=candidate_id,
        skill_name=question_obj.skill,
        new_score=new_score
    )

    # Save attempt to DB
    attempt_id = db.save_attempt(
        question_id=req.question_id,
        candidate_id=candidate_id,
        skill=question_obj.skill,
        topic=question_obj.topic,
        difficulty=question_obj.difficulty,
        question=question_obj.question,
        answer=req.answer,
        evaluation=evaluation
    )

    # Re-calculate next adaptive recommendation
    updated_skills = db.get_candidate_skills(candidate_id)
    updated_attempts = db.get_candidate_attempts(candidate_id, limit=5)
    
    updated_gaps = []
    for s in updated_skills:
        if s.score < 70 and (s.required or s.preferred):
            priority = 1 if (s.required and s.score == 0) else (2 if s.required else 4)
            updated_gaps.append(GapItem(
                skill_name=s.skill_name,
                score=s.score,
                importance="required" if s.required else "preferred",
                priority=priority,
                reason="Practice needed"
            ))
    updated_gaps.sort(key=lambda g: (g.priority, g.score))

    next_rec = adaptive_planner.recommend_next_step(
        gaps=updated_gaps,
        skills=updated_skills,
        recent_attempts=updated_attempts
    )

    return EvaluationResponse(
        attempt_id=attempt_id,
        skill=question_obj.skill,
        topic=question_obj.topic,
        question=question_obj.question,
        answer=req.answer,
        score=evaluation.score,
        correctness=evaluation.correctness,
        missing_concepts=evaluation.missing_concepts,
        feedback=evaluation.feedback,
        previous_skill_score=previous_score,
        new_skill_score=new_score,
        recommended_next_topic=evaluation.recommended_next_topic,
        next_recommendation=next_rec
    )
