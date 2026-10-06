import math
from typing import List, Dict, Tuple, Set
from app.knowledge.skill_taxonomy import skill_taxonomy
from app.schemas import SkillItem, GapItem, ResumeAnalysis, JobAnalysis


class GapAnalyzer:
    """
    Deterministic Skill Gap Analyzer and Readiness Engine.
    Separates deterministic application mathematics from LLM linguistic parsing.
    """

    @staticmethod
    def calculate_initial_baseline(
        skill_name: str,
        resume_analysis: ResumeAnalysis,
        match_type: str = "none"
    ) -> int:
        """
        Calculates a transparent, deterministic initial baseline score:
        - 80: Explicitly stated in resume AND mentioned in project descriptions.
        - 72: Explicitly stated in technical skills list.
        - 65: Related taxonomy match (e.g. child implementation for a required category).
        - 0:  Not found / missing.
        """
        skill_lower = skill_name.lower()
        projects_text = " ".join(resume_analysis.projects).lower()
        
        # Check if explicitly in resume technical skills
        in_skills = any(
            skill_lower == s.lower() or skill_taxonomy.normalize(s).lower() == skill_lower
            for s in resume_analysis.technical_skills
        )
        
        # Check if mentioned in projects
        in_projects = skill_lower in projects_text

        if in_skills and in_projects:
            return 80
        elif in_skills:
            return 72
        elif match_type in ["taxonomy_child", "taxonomy_parent"]:
            return 65
        else:
            return 0

    @classmethod
    def analyze_gaps(
        cls,
        resume_analysis: ResumeAnalysis,
        job_analysis: JobAnalysis
    ) -> Tuple[List[SkillItem], List[str], List[GapItem], int]:
        """
        Performs deterministic matching, calculates gap priorities, and computes readiness.
        
        Returns:
            all_skills: List[SkillItem]
            matched_job_skills: List[str]
            gaps: List[GapItem] (sorted by priority)
            readiness: int (0 to 100)
        """
        all_skills: Dict[str, SkillItem] = {}
        matched_job_skills: Set[str] = set()
        
        candidate_skills = [skill_taxonomy.normalize(s) for s in resume_analysis.technical_skills]
        required_skills = [skill_taxonomy.normalize(s) for s in job_analysis.required_skills]
        preferred_skills = [skill_taxonomy.normalize(s) for s in job_analysis.preferred_skills]

        # 1. Process Candidate's Resume Skills
        for cand_skill in candidate_skills:
            if not cand_skill:
                continue
            
            # Check if this candidate skill satisfies any required or preferred job skill
            is_req = False
            is_pref = False
            is_matched = False

            for req in required_skills:
                matches, _ = skill_taxonomy.matches_requirement(cand_skill, req)
                if matches:
                    is_req = True
                    is_matched = True
                    matched_job_skills.add(req)

            for pref in preferred_skills:
                matches, _ = skill_taxonomy.matches_requirement(cand_skill, pref)
                if matches:
                    is_pref = True
                    is_matched = True
                    matched_job_skills.add(pref)

            score = cls.calculate_initial_baseline(cand_skill, resume_analysis)
            status = "strong" if score >= 70 else ("moderate" if score >= 50 else "gap")

            all_skills[cand_skill] = SkillItem(
                skill_name=cand_skill,
                score=score,
                required=is_req,
                preferred=is_pref,
                source="resume",
                matched=is_matched,
                status=status
            )

        # 2. Process Required Job Skills (Identify missing or taxonomy-matched)
        for req in required_skills:
            if not req:
                continue
            
            # Check if already present from resume
            if req in all_skills:
                all_skills[req].required = True
                all_skills[req].matched = True
                continue

            # Check if satisfied by any candidate skill via taxonomy
            matched_via_child = False
            best_match_type = "none"
            for cand_skill in candidate_skills:
                matches, m_type = skill_taxonomy.matches_requirement(cand_skill, req)
                if matches:
                    matched_via_child = True
                    best_match_type = m_type
                    matched_job_skills.add(req)
                    break

            if matched_via_child:
                score = cls.calculate_initial_baseline(req, resume_analysis, match_type=best_match_type)
                status = "strong" if score >= 70 else "moderate"
                all_skills[req] = SkillItem(
                    skill_name=req,
                    score=score,
                    required=True,
                    preferred=False,
                    source="job_required",
                    matched=True,
                    status=status
                )
            else:
                # Completely missing required skill
                all_skills[req] = SkillItem(
                    skill_name=req,
                    score=0,
                    required=True,
                    preferred=False,
                    source="job_required",
                    matched=False,
                    status="gap"
                )

        # 3. Process Preferred Job Skills (Identify missing or taxonomy-matched)
        for pref in preferred_skills:
            if not pref:
                continue
            
            if pref in all_skills:
                all_skills[pref].preferred = True
                all_skills[pref].matched = True
                continue

            matched_via_child = False
            best_match_type = "none"
            for cand_skill in candidate_skills:
                matches, m_type = skill_taxonomy.matches_requirement(cand_skill, pref)
                if matches:
                    matched_via_child = True
                    best_match_type = m_type
                    matched_job_skills.add(pref)
                    break

            if matched_via_child:
                score = cls.calculate_initial_baseline(pref, resume_analysis, match_type=best_match_type)
                all_skills[pref] = SkillItem(
                    skill_name=pref,
                    score=score,
                    required=False,
                    preferred=True,
                    source="job_preferred",
                    matched=True,
                    status="strong" if score >= 70 else "moderate"
                )
            else:
                all_skills[pref] = SkillItem(
                    skill_name=pref,
                    score=0,
                    required=False,
                    preferred=True,
                    source="job_preferred",
                    matched=False,
                    status="gap"
                )

        # 4. Identify Gaps & Assign Priority
        gaps: List[GapItem] = []
        for skill_name, item in all_skills.items():
            # Only required or preferred skills count towards job gaps
            if not (item.required or item.preferred):
                continue

            if item.score < 70 or not item.matched:
                # Calculate priority
                if item.required and item.score == 0:
                    priority = 1
                    reason = f"Required by job description but not demonstrated in resume."
                elif item.required and item.score < 50:
                    priority = 2
                    reason = f"Required core skill with low initial baseline ({item.score}%)."
                elif item.required:
                    priority = 3
                    reason = f"Required skill that needs deeper practice ({item.score}%)."
                elif item.preferred and item.score == 0:
                    priority = 4
                    reason = f"Preferred skill not found in resume; practicing gives competitive edge."
                elif item.preferred and item.score < 50:
                    priority = 5
                    reason = f"Preferred skill with low baseline ({item.score}%)."
                else:
                    priority = 6
                    reason = f"Preferred skill with moderate proficiency ({item.score}%)."

                gaps.append(GapItem(
                    skill_name=skill_name,
                    score=item.score,
                    importance="required" if item.required else "preferred",
                    priority=priority,
                    reason=reason
                ))

        # Sort gaps by priority ascending (1 is highest priority), then score ascending
        gaps.sort(key=lambda g: (g.priority, g.score))

        # 5. Compute Explainable Readiness Percentage
        readiness = cls.calculate_readiness(required_skills, preferred_skills, all_skills)

        return list(all_skills.values()), list(matched_job_skills), gaps, readiness

    @staticmethod
    def calculate_readiness(
        required_skills: List[str],
        preferred_skills: List[str],
        skills_map: Dict[str, SkillItem]
    ) -> int:
        """
        Explainable Readiness Formula:
        - 70% weight allocated to Required Skills coverage.
        - 30% weight allocated to Preferred Skills coverage.
        - If no preferred skills exist, 100% weight is given to required skills.
        - If neither exists, returns 50% baseline.
        """
        if not required_skills and not preferred_skills:
            return 50

        req_scores = [skills_map[s].score for s in required_skills if s in skills_map]
        pref_scores = [skills_map[s].score for s in preferred_skills if s in skills_map]

        req_avg = sum(req_scores) / len(req_scores) if req_scores else 0.0
        pref_avg = sum(pref_scores) / len(pref_scores) if pref_scores else 0.0

        if required_skills and preferred_skills:
            readiness_float = (req_avg * 0.70) + (pref_avg * 0.30)
        elif required_skills:
            readiness_float = req_avg
        else:
            readiness_float = pref_avg

        return max(0, min(100, int(round(readiness_float))))


gap_analyzer = GapAnalyzer()
