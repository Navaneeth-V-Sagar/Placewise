import logging
from app.ai.client import ai_client
from app.ai.prompts import RESUME_EXTRACTION_SYSTEM, RESUME_EXTRACTION_PROMPT
from app.schemas import ResumeAnalysis
from app.knowledge.skill_taxonomy import skill_taxonomy

logger = logging.getLogger("placewise.analyzer.resume")


class ResumeAnalyzer:
    @staticmethod
    async def analyze(resume_text: str) -> ResumeAnalysis:
        """
        Extracts structured technical skills and projects from resume text using Qwen3
        and normalizes skills deterministically via skill taxonomy.
        """
        if not resume_text or len(resume_text.strip()) == 0:
            return ResumeAnalysis(technical_skills=[], projects=[])

        prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text)
        
        # Extract via LLM with Pydantic schema validation
        raw_result = await ai_client.generate_structured(
            prompt=prompt,
            response_model=ResumeAnalysis,
            system_prompt=RESUME_EXTRACTION_SYSTEM
        )

        # Deterministically normalize and deduplicate extracted skill names
        normalized_skills = []
        seen = set()
        for s in raw_result.technical_skills:
            norm = skill_taxonomy.normalize(s)
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                normalized_skills.append(norm)

        return ResumeAnalysis(
            technical_skills=normalized_skills,
            projects=raw_result.projects
        )


resume_analyzer = ResumeAnalyzer()
