import pytest
from app.knowledge.skill_taxonomy import skill_taxonomy, SkillTaxonomy
from app.services.gap_analyzer import gap_analyzer, GapAnalyzer
from app.schemas import ResumeAnalysis, JobAnalysis


def test_taxonomy_normalization():
    assert skill_taxonomy.normalize("fastapi") == "FastAPI"
    assert skill_taxonomy.normalize("postgres") == "PostgreSQL"
    assert skill_taxonomy.normalize("postgresql") == "PostgreSQL"
    assert skill_taxonomy.normalize("sklearn") == "scikit-learn"
    assert skill_taxonomy.normalize("k8s") == "Kubernetes"
    assert skill_taxonomy.normalize("docker") == "Docker"
    assert skill_taxonomy.normalize("ts") == "TypeScript"
    assert skill_taxonomy.normalize("reactjs") == "React"


def test_taxonomy_relationship_matching():
    # FastAPI satisfies REST APIs
    matches, match_type = skill_taxonomy.matches_requirement("FastAPI", "REST APIs")
    assert matches is True
    assert match_type == "taxonomy_child"

    # PostgreSQL satisfies SQL
    matches, match_type = skill_taxonomy.matches_requirement("PostgreSQL", "SQL")
    assert matches is True

    # MongoDB does NOT satisfy SQL or Docker
    matches, match_type = skill_taxonomy.matches_requirement("MongoDB", "SQL")
    assert matches is False
    assert match_type == "none"


def test_gap_analysis_matching_and_irrelevant_skills():
    resume = ResumeAnalysis(
        technical_skills=["Python", "FastAPI", "MongoDB"],
        projects=["Built a high-traffic REST backend with Python and FastAPI."]
    )
    job = JobAnalysis(
        required_skills=["Python", "REST APIs", "SQL"],
        preferred_skills=["Docker"]
    )

    all_skills, matched_job_skills, gaps, readiness = gap_analyzer.analyze_gaps(resume, job)

    skills_by_name = {s.skill_name: s for s in all_skills}

    # 1. Python should be matched, score 80 (in skills + in projects)
    assert "Python" in skills_by_name
    assert skills_by_name["Python"].score == 80
    assert skills_by_name["Python"].matched is True
    assert skills_by_name["Python"].required is True

    # 2. REST APIs should be matched via FastAPI child
    assert "REST APIs" in matched_job_skills

    # 3. MongoDB is in resume, but NOT required/preferred by the job -> matched=False
    assert "MongoDB" in skills_by_name
    assert skills_by_name["MongoDB"].matched is False
    assert skills_by_name["MongoDB"].required is False
    assert skills_by_name["MongoDB"].preferred is False
    # MongoDB should NOT appear in gaps because it's not a job requirement
    assert not any(g.skill_name == "MongoDB" for g in gaps)

    # 4. SQL is required and missing -> score = 0, priority = 1
    assert "SQL" in skills_by_name
    assert skills_by_name["SQL"].score == 0
    sql_gap = next((g for g in gaps if g.skill_name == "SQL"), None)
    assert sql_gap is not None
    assert sql_gap.priority == 1
    assert sql_gap.importance == "required"

    # 5. Docker is preferred and missing -> score = 0, priority = 4
    docker_gap = next((g for g in gaps if g.skill_name == "Docker"), None)
    assert docker_gap is not None
    assert docker_gap.priority == 4
    assert docker_gap.importance == "preferred"

    # 6. Priority order: SQL (required missing) must come before Docker (preferred missing)
    gap_names = [g.skill_name for g in gaps]
    assert gap_names.index("SQL") < gap_names.index("Docker")

    # 7. Readiness check
    assert 0 <= readiness <= 100
