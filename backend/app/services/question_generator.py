import logging
import re
from typing import Optional
from app.ai.client import ai_client
from app.ai.prompts import QUESTION_GENERATION_SYSTEM, QUESTION_GENERATION_PROMPT
from app.schemas import Question, PlannerRecommendation

logger = logging.getLogger("placewise.generator.question")


class QuestionGenerator:
    @staticmethod
    def clean_question_text(raw_q: str, skill: str, topic: str) -> str:
        """
        Removes any residual LLM meta-commentary, thinking artifacts, or preambles
        (e.g., 'Okay, let's tackle this...', 'The user wants...', 'First, I need to...').
        """
        if not raw_q:
            return f"Explain the core principles, common implementation patterns, and trade-offs of {topic} in {skill}."

        cleaned = raw_q.strip()

        # Remove leading JSON or markdown artifacts if any leaked into the string
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Check quoted strings for valid questions
        quoted_matches = re.findall(r'"([^"\n\r]{20,})"', cleaned)
        for q in reversed(quoted_matches):
            if "?" in q or any(q.lower().startswith(w) for w in ["what", "how", "explain", "why", "describe", "write", "you are", "suppose", "design", "consider"]):
                return q.strip()

        # Remove typical meta-commentary preambles
        preamble_patterns = [
            r"^(?:Okay|Sure|First|Here is|Let'?s|Wait|The user|Note|I will|So|How about|Question)[^\n\.\?:]*[\n\.\?:]+\s*",
        ]
        for _ in range(5):
            prev = cleaned
            for pat in preamble_patterns:
                cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
            if cleaned == prev:
                break

        # Unquote surrounding double or single quotes if present
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
            cleaned = cleaned[1:-1].strip()

        # If the cleaned text still appears to be an unparsed thinking monologue
        if any(cleaned.lower().startswith(p) for p in ["okay", "first,", "the user", "let's formulate", "i will generate", "wait,", "so maybe", "for example:"]):
            sentences = [s.strip() for s in re.split(r'[\n\r]+|[.!?]\s+', cleaned) if s.strip()]
            valid_qs = [s for s in sentences if s.endswith("?") or s.lower().startswith(("explain", "write", "how", "what", "design", "compare", "implement", "you are"))]
            if valid_qs:
                cleaned = valid_qs[-1]
                if not cleaned.endswith("?"):
                    cleaned += "?"
            else:
                cleaned = f"In the context of {skill}, explain how {topic} works in production systems and describe key edge cases to handle."

        return cleaned.strip()

    @classmethod
    async def generate_question(
        cls,
        target_role: str,
        recommendation: PlannerRecommendation,
        previous_mistakes: Optional[str] = None
    ) -> Question:
        """
        Generates an adaptive interview question targeted at the candidate's specific
        weakness and subtopic using Qwen3.
        """
        # Parse focus skill deterministically from recommendation (e.g. "SQL (Score: 0%)" -> "SQL")
        raw_skill = recommendation.current_weakness.split("(")[0].strip()
        skill_name = raw_skill if raw_skill and raw_skill not in ["Technical", "General", "Core Skills"] else "REST APIs"
        topic = recommendation.recommended_topic or f"{skill_name} Fundamentals"
        difficulty = recommendation.difficulty or "Intermediate"
        reason = recommendation.reason
        mistake_ctx = previous_mistakes or "No prior mistakes recorded; candidate is starting this topic."

        prompt = QUESTION_GENERATION_PROMPT.format(
            target_role=target_role or "Software Engineer",
            skill=skill_name,
            topic=topic,
            difficulty=difficulty,
            reason=reason,
            mistake_context=mistake_ctx
        )

        question_obj = await ai_client.generate_structured(
            prompt=prompt,
            response_model=Question,
            system_prompt=QUESTION_GENERATION_SYSTEM
        )

        # Strictly enforce deterministic planner targets on the question object
        question_obj.skill = skill_name
        question_obj.topic = topic
        question_obj.difficulty = difficulty

        # Clean any raw preamble/meta-commentary from the question string
        question_obj.question = cls.clean_question_text(question_obj.question, skill_name, topic)

        return question_obj


question_generator = QuestionGenerator()
