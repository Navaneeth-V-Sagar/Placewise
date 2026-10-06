from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
import logging
from app.services.resume_parser import resume_parser, ResumeParserError
from app.services.resume_analyzer import resume_analyzer
from app.services.job_analyzer import job_analyzer
from app.services.gap_analyzer import gap_analyzer
from app.services.planner import adaptive_planner
from app.database import db
from app.schemas import AnalysisResponse, JobAnalysis

router = APIRouter(tags=["Analysis"])
logger = logging.getLogger("placewise.api.analysis")


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_profile(
    resume: UploadFile = File(..., description="PDF Resume file"),
    target_role: str = Form(..., description="Target Job Role (e.g. AI Engineer, Full Stack Developer)"),
    job_description: str = Form(..., description="Full Job Description text")
):
    """
    Core Entrypoint:
    1. Extracts text from uploaded PDF resume via PyMuPDF.
    2. Runs Qwen3 structured extraction on Resume and Job Description.
    3. Executes deterministic Skill Taxonomy matching, Gap Analysis, and Readiness calculation.
    4. Persists Candidate, Job, and Skills state in SQLite.
    5. Generates initial adaptive Planner recommendation.
    """
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume files (.pdf) are supported."
        )

    # 1. Extract resume text via PyMuPDF
    try:
        content = await resume.read()
        resume_text = resume_parser.extract_text_from_bytes(content)
    except ResumeParserError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Resume reading error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process resume file.")

    # 2. Extract structured entities via LLM
    try:
        resume_analysis = await resume_analyzer.analyze(resume_text)
        job_analysis = await job_analyzer.analyze(target_role, job_description)
    except Exception as e:
        logger.error(f"AI Extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI model inference error: {str(e)}"
        )

    # 3. Deterministic Skill Gap Analysis & Readiness calculation
    all_skills, matched_skills, gaps, readiness = gap_analyzer.analyze_gaps(
        resume_analysis=resume_analysis,
        job_analysis=job_analysis
    )

    # 4. Generate initial adaptive recommendation
    recommendation = adaptive_planner.recommend_next_step(
        gaps=gaps,
        skills=all_skills,
        recent_attempts=[]
    )

    # 5. Extract Candidate Name from first line or default
    first_line = resume_text.splitlines()[0].strip() if resume_text.splitlines() else "Candidate"
    candidate_name = first_line[:50] if len(first_line) > 2 else "Candidate"

    # 6. Persist to SQLite
    try:
        candidate_id = db.create_candidate(
            name=candidate_name,
            target_role=target_role,
            resume_text=resume_text,
            projects=resume_analysis.projects
        )

        db.create_job(
            candidate_id=candidate_id,
            target_role=target_role,
            description=job_description,
            required_skills=job_analysis.required_skills,
            preferred_skills=job_analysis.preferred_skills
        )

        db.save_skills(candidate_id=candidate_id, skills=all_skills)
    except Exception as e:
        logger.error(f"Database persistence error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save candidate state.")

    return AnalysisResponse(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        target_role=target_role,
        extracted_skills=resume_analysis.technical_skills,
        projects=resume_analysis.projects,
        required_skills=job_analysis.required_skills,
        preferred_skills=job_analysis.preferred_skills,
        matched_skills=matched_skills,
        skill_gaps=gaps,
        readiness=readiness,
        recommended_focus=recommendation
    )
