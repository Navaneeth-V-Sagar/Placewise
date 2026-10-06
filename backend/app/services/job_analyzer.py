import logging
from app.ai.client import ai_client
from app.ai.prompts import JOB_ANALYSIS_SYSTEM, JOB_ANALYSIS_PROMPT
from app.schemas import JobAnalysis
from app.knowledge.skill_taxonomy import skill_taxonomy

logger = logging.getLogger("placewise.analyzer.job")


class JobAnalyzer:
    @staticmethod
    async def analyze(target_role: str, job_description: str) -> JobAnalysis:
        """
        Extracts required and preferred skills from a job description using Qwen3
        and normalizes skills deterministically via skill taxonomy.
        """
        if not job_description or len(job_description.strip()) == 0:
            return JobAnalysis(required_skills=[], preferred_skills=[])

        prompt = JOB_ANALYSIS_PROMPT.format(
            target_role=target_role or "Software Engineer",
            job_description=job_description
        )

        # Extract via LLM with Pydantic schema validation
        raw_result = await ai_client.generate_structured(
            prompt=prompt,
            response_model=JobAnalysis,
            system_prompt=JOB_ANALYSIS_SYSTEM
        )

        # Deterministically normalize and deduplicate required skills
        norm_required = []
        seen = set()
        for s in raw_result.required_skills:
            norm = skill_taxonomy.normalize(s)
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                norm_required.append(norm)

        # Deterministically normalize and deduplicate preferred skills
        norm_preferred = []
        for s in raw_result.preferred_skills:
            norm = skill_taxonomy.normalize(s)
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                norm_preferred.append(norm)

        return JobAnalysis(
            required_skills=norm_required,
            preferred_skills=norm_preferred
        )


job_analyzer = JobAnalyzer()
