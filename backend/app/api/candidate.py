from fastapi import APIRouter, HTTPException, status
from app.database import db
from app.services.gap_analyzer import gap_analyzer
from app.services.planner import adaptive_planner
from app.schemas import (
    CandidateProfile,
    ProgressResponse,
    ResumeAnalysis,
    JobAnalysis,
    GapItem
)

router = APIRouter(tags=["Candidate"])


@router.get("/candidate/{candidate_id}", response_model=CandidateProfile)
async def get_candidate_profile(candidate_id: int):
    candidate = db.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found."
        )

    skills = db.get_candidate_skills(candidate_id)
    return CandidateProfile(
        id=candidate["id"],
        name=candidate["name"],
        target_role=candidate["target_role"],
        created_at=candidate["created_at"],
        skills=skills,
        projects=candidate["projects"]
    )


@router.get("/candidate/{candidate_id}/progress", response_model=ProgressResponse)
async def get_candidate_progress(candidate_id: int):
    candidate = db.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found."
        )

    job = db.get_job_by_candidate(candidate_id)
    skills = db.get_candidate_skills(candidate_id)
    attempts = db.get_candidate_attempts(candidate_id, limit=10)

    # Re-calculate gaps and readiness based on latest skill scores
    required_skills = job["required_skills"] if job else []
    preferred_skills = job["preferred_skills"] if job else []

    skills_map = {s.skill_name: s for s in skills}
    readiness = gap_analyzer.calculate_readiness(required_skills, preferred_skills, skills_map)

    # Calculate current gaps
    gaps = []
    strong_skills = []
    for s in skills:
        if s.score >= 70:
            strong_skills.append(s)
        elif s.required or s.preferred:
            priority = 1 if (s.required and s.score == 0) else (2 if s.required else 4)
            gaps.append(GapItem(
                skill_name=s.skill_name,
                score=s.score,
                importance="required" if s.required else "preferred",
                priority=priority,
                reason="Practice needed to reach mastery benchmark."
            ))

    gaps.sort(key=lambda g: (g.priority, g.score))

    # Calculate latest adaptive recommendation
    current_rec = adaptive_planner.recommend_next_step(
        gaps=gaps,
        skills=skills,
        recent_attempts=attempts
    )

    return ProgressResponse(
        candidate_id=candidate["id"],
        target_role=candidate["target_role"],
        readiness=readiness,
        strong_skills=strong_skills,
        skill_gaps=gaps,
        recent_attempts=attempts,
        current_recommendation=current_rec
    )
