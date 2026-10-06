from typing import List, Optional, Dict
from app.schemas import (
    SkillItem,
    GapItem,
    PlannerRecommendation,
    QuestionAttemptItem
)

# Skill subtopic mapping for granular adaptive recommendations
SKILL_SUBTOPICS: Dict[str, List[str]] = {
    "SQL": ["LEFT JOIN & NULL Handling", "INNER vs OUTER JOINs", "GROUP BY & HAVING clauses", "Window Functions (ROW_NUMBER, RANK)", "Indexing & Query Optimization"],
    "PostgreSQL": ["JSONB queries & indexing", "Connection Pooling & Transactions", "EXPLAIN ANALYZE tuning"],
    "MySQL": ["InnoDB vs MyISAM locking", "Query indexing strategies"],
    "REST APIs": ["Idempotency & HTTP Methods (PUT vs POST vs PATCH)", "Status Codes & Error Handling Standards", "Rate Limiting & Authentication Headers", "Pagination & Filtering Design"],
    "FastAPI": ["Dependency Injection & Yield fixtures", "Pydantic request/response validation", "Async route handlers & background tasks"],
    "Flask": ["Application Factories & Blueprints", "WSGI vs ASGI middleware"],
    "Docker": ["Multi-stage Dockerfile builds", "Layer caching optimization", "Port mapping & volume persistence", "Container networking"],
    "Kubernetes": ["Pods vs Deployments vs Services", "Resource requests & limits", "ConfigMaps & Secrets"],
    "Python": ["Generators & Memory Efficiency", "Decorators & Closures", "GIL (Global Interpreter Lock) & Concurrency", "Context Managers (__enter__/__exit__)"],
    "JavaScript": ["Event Loop & Microtasks", "Promises & Async/Await Error Handling", "Closures & Prototype Inheritance"],
    "TypeScript": ["Generics & Type Constraints", "Union vs Intersection Types", "Utility Types (Partial, Record, Pick)"],
    "React": ["useEffect lifecycle & dependency arrays", "Custom Hooks & State Management", "Component Re-rendering & useMemo/useCallback"],
    "Machine Learning": ["Bias-Variance Tradeoff & Regularization", "Evaluation Metrics (Precision/Recall vs ROC-AUC)", "Feature Engineering & Imputation"],
    "Deep Learning": ["Vanishing Gradients & Activation Functions", "Backpropagation & Learning Rates", "CNN Pooling & Stride architectures"],
    "Git": ["Git Rebase vs Merge", "Resolving merge conflicts & Cherry-picking"],
}


class AdaptivePlanner:
    """
    Deterministic Adaptive Learning Loop Planner.
    Analyzes candidate skill state, gap priorities, and recent mistake history
    to calculate targeted next study topics and difficulty levels.
    """

    @classmethod
    def recommend_next_step(
        cls,
        gaps: List[GapItem],
        skills: List[SkillItem],
        recent_attempts: Optional[List[QuestionAttemptItem]] = None
    ) -> PlannerRecommendation:
        """
        Calculates the next adaptive recommendation:
        1. If recent attempt scored poorly (<60), prioritize immediate targeted remediation of missed concepts.
        2. Otherwise, select the highest priority skill gap (priority 1 = required missing, etc.).
        3. If no gaps exist (all skills > 70%), recommend mastery topic at Advanced difficulty.
        """
        recent_attempts = recent_attempts or []
        last_attempt = recent_attempts[-1] if len(recent_attempts) > 0 else None

        # 1. Check if candidate recently struggled with a question (<65 score)
        if last_attempt and last_attempt.score is not None and last_attempt.score < 65:
            skill_name = last_attempt.skill
            # Reject generic legacy labels if present
            if skill_name and skill_name not in ["Technical", "General", "Core Skills", ""]:
                missing = ", ".join(last_attempt.missing_concepts) if last_attempt.missing_concepts else "core fundamentals"
                recommended_topic = last_attempt.recommended_next_topic or f"{last_attempt.topic} - Remediation"
                
                return PlannerRecommendation(
                    current_weakness=f"{skill_name} ({last_attempt.topic})",
                    recommended_topic=recommended_topic,
                    difficulty="Beginner" if last_attempt.score < 40 else "Intermediate",
                    reason=f"Recently struggled on '{last_attempt.topic}' (scored {last_attempt.score}/100). Focus on missed concepts: {missing}.",
                    next_action=f"Practice targeted questions on {recommended_topic}."
                )

        # 2. Pick top priority gap from the gaps list
        if gaps:
            # Filter out any generic labels
            valid_gaps = [g for g in gaps if g.skill_name not in ["Technical", "General", "Core Skills"]]
            top_gap = valid_gaps[0] if valid_gaps else gaps[0]
            skill_name = top_gap.skill_name
            subtopics = SKILL_SUBTOPICS.get(skill_name, [f"{skill_name} Fundamentals", f"{skill_name} Applied Scenarios"])
            
            # Choose appropriate subtopic based on past attempts
            attempted_topics = [a.topic for a in recent_attempts if a.skill == skill_name]
            unattempted = [t for t in subtopics if t not in attempted_topics]
            selected_topic = unattempted[0] if unattempted else subtopics[0]

            difficulty = "Beginner" if top_gap.score == 0 else "Intermediate"
            
            importance_str = "Required job requirement" if top_gap.importance == "required" else "Preferred job skill"
            return PlannerRecommendation(
                current_weakness=f"{skill_name} (Score: {top_gap.score}%)",
                recommended_topic=selected_topic,
                difficulty=difficulty,
                reason=f"{importance_str} with critical gap ({top_gap.reason}).",
                next_action=f"Start with conceptual application question on {selected_topic}."
            )

        # 3. If no critical gaps, find lowest score among current skills or recommend mastery
        valid_skills = [s for s in skills if s.skill_name not in ["Technical", "General", "Core Skills"]]
        if valid_skills:
            lowest_skill = min(valid_skills, key=lambda s: s.score)
            subtopics = SKILL_SUBTOPICS.get(lowest_skill.skill_name, [f"{lowest_skill.skill_name} Fundamentals", f"{lowest_skill.skill_name} Applied Scenarios"])
            selected_topic = subtopics[-1] if len(subtopics) > 1 else subtopics[0]
            
            return PlannerRecommendation(
                current_weakness=f"{lowest_skill.skill_name} (Current Score: {lowest_skill.score}%)",
                recommended_topic=selected_topic,
                difficulty="Advanced",
                reason=f"Solid foundational coverage achieved. Advance to higher-complexity interview scenarios.",
                next_action=f"Practice advanced technical design question on {selected_topic}."
            )

        # Concrete default fallback
        return PlannerRecommendation(
            current_weakness="REST APIs (Score: 0%)",
            recommended_topic="REST API Fundamentals & HTTP Methods",
            difficulty="Beginner",
            reason="Core prerequisite for modern backend and AI systems engineering.",
            next_action="Practice fundamental REST API design principles."
        )


adaptive_planner = AdaptivePlanner()
