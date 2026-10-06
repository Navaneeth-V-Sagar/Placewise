import logging
from typing import Tuple, List, Optional
from app.ai.client import ai_client
from app.ai.prompts import EVALUATION_SYSTEM, EVALUATION_PROMPT
from app.schemas import Evaluation, Question

logger = logging.getLogger("placewise.evaluator")


class AnswerEvaluator:
    """
    Evaluates candidate responses using Qwen3 and updates skill mastery
    using the deterministic formula: new_score = round(0.7 * prev + 0.3 * current).
    """

    @staticmethod
    def calculate_updated_score(previous_score: int, answer_score: int) -> int:
        """
        Deterministic scoring formula (Section 18):
        new_score = 0.7 * previous_score + 0.3 * answer_score
        Bounded between 0 and 100.
        """
        raw_new = (0.70 * float(previous_score)) + (0.30 * float(answer_score))
        return max(0, min(100, int(round(raw_new))))

    @classmethod
    async def evaluate_answer(
        cls,
        question: Question,
        candidate_answer: str,
        previous_score: int = 0
    ) -> Tuple[Evaluation, int]:
        """
        Evaluates candidate answer against the question and expected technical depth.
        Returns (Evaluation, new_skill_score).
        """
        if not candidate_answer or len(candidate_answer.strip()) == 0:
            # Handle empty answer deterministically without LLM overhead
            eval_result = Evaluation(
                score=0,
                correctness="Incorrect",
                missing_concepts=["No answer provided by candidate."],
                feedback="You did not submit an answer for this question. Review the question requirements and practice the core concepts.",
                recommended_next_topic=question.topic
            )
            new_score = cls.calculate_updated_score(previous_score, 0)
            return eval_result, new_score

        prompt = EVALUATION_PROMPT.format(
            skill=question.skill,
            topic=question.topic,
            question=question.question,
            candidate_answer=candidate_answer
        )

        eval_result = await ai_client.generate_structured(
            prompt=prompt,
            response_model=Evaluation,
            system_prompt=EVALUATION_SYSTEM
        )

        # Enforce bounds on score
        eval_result.score = max(0, min(100, eval_result.score))

        # Calculate new deterministic skill score
        new_score = cls.calculate_updated_score(previous_score, eval_result.score)

        return eval_result, new_score


answer_evaluator = AnswerEvaluator()
