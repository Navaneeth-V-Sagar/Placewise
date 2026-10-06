import re
from typing import Dict, List, Set, Optional, Tuple


# Canonical aliases dictionary: maps lowercase variation -> canonical display name
ALIAS_MAP: Dict[str, str] = {
    # Languages
    "python": "Python",
    "py": "Python",
    "python3": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "sql": "SQL",

    # Web & APIs
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "django rest framework": "Django REST Framework",
    "drf": "Django REST Framework",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "grpc": "gRPC",

    # Frontend
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",

    # Databases & Storage
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",

    # Machine Learning & AI
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "xgboost": "XGBoost",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "cnn": "CNN",
    "rnn": "RNN",
    "transformer": "Transformers",
    "transformers": "Transformers",
    "llm": "LLMs",
    "llms": "LLMs",
    "ollama": "Ollama",

    # DevOps & Tools
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
}

# Taxonomy relationships: Parent Category -> list of Subskills / Implementations
TAXONOMY_TREE: Dict[str, List[str]] = {
    "REST APIs": ["FastAPI", "Flask", "Express.js", "Django REST Framework", "gRPC", "GraphQL"],
    "Machine Learning": ["scikit-learn", "XGBoost", "TensorFlow", "PyTorch", "Pandas", "NumPy"],
    "Deep Learning": ["TensorFlow", "PyTorch", "Keras", "CNN", "RNN", "Transformers"],
    "Relational Databases": ["PostgreSQL", "MySQL", "SQLite", "SQL"],
    "SQL": ["PostgreSQL", "MySQL", "SQLite"],
    "NoSQL": ["MongoDB", "Redis", "Cassandra", "Elasticsearch"],
    "Version Control": ["Git", "GitHub", "GitLab"],
    "Containerization": ["Docker", "Kubernetes"],
    "Cloud Computing": ["AWS", "GCP", "Azure"],
    "Frontend Development": ["React", "Vue.js", "Angular", "Next.js", "HTML", "CSS", "JavaScript", "TypeScript"],
}


class SkillTaxonomy:
    @classmethod
    def normalize(cls, skill: str) -> str:
        """
        Normalizes a skill name to its canonical display form.
        e.g., 'fastapi' -> 'FastAPI', 'Strong Python' -> 'Python', 'postgres' -> 'PostgreSQL'.
        """
        if not skill:
            return ""
        
        cleaned = skill.strip()

        # Strip common descriptive qualifier prefixes
        prefixes_to_strip = [
            r"^strong\s+",
            r"^deep\s+experience\s+in\s+",
            r"^experience\s+with\s+",
            r"^knowledge\s+of\s+",
            r"^familiarity\s+with\s+",
            r"^proficiency\s+in\s+",
            r"^hands-on\s+",
            r"^solid\s+",
        ]
        for p in prefixes_to_strip:
            cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE).strip()

        cleaned_lower = cleaned.lower()

        # Direct alias lookup
        if cleaned_lower in ALIAS_MAP:
            return ALIAS_MAP[cleaned_lower]

        # Check if punctuation-stripped matches
        alphanumeric = re.sub(r'[^a-zA-Z0-9+#]', '', cleaned_lower)
        if alphanumeric in ALIAS_MAP:
            return ALIAS_MAP[alphanumeric]

        # Default: Title Case if no specific alias is registered
        return cleaned.title()

    @classmethod
    def get_related_skills(cls, canonical_skill: str) -> Set[str]:
        """
        Returns all related skills (children or parent category members).
        """
        related: Set[str] = set()
        
        # 1. If canonical_skill is a parent in taxonomy, add all its children
        if canonical_skill in TAXONOMY_TREE:
            related.update(TAXONOMY_TREE[canonical_skill])

        # 2. If canonical_skill is a child, add its parents and sibling skills
        for parent, children in TAXONOMY_TREE.items():
            if canonical_skill in children or canonical_skill.lower() in [c.lower() for c in children]:
                related.add(parent)
                related.update(children)

        return related

    @classmethod
    def matches_requirement(cls, candidate_skill: str, job_skill: str) -> Tuple[bool, str]:
        """
        Determines whether a candidate's skill satisfies a job requirement.
        Returns (is_match: bool, match_type: str).
        match_type can be 'exact', 'taxonomy_child', 'taxonomy_parent', or 'none'.
        """
        cand_norm = cls.normalize(candidate_skill)
        job_norm = cls.normalize(job_skill)

        # 1. Exact canonical match
        if cand_norm.lower() == job_norm.lower():
            return True, "exact"

        # 2. Check if candidate skill satisfies the job requirement via taxonomy
        # e.g., Job requires "REST APIs" and candidate has "FastAPI" -> child satisfies parent requirement
        if job_norm in TAXONOMY_TREE and cand_norm in TAXONOMY_TREE[job_norm]:
            return True, "taxonomy_child"

        # e.g., Job requires "SQL" and candidate has "PostgreSQL" -> specific satisfies general
        if job_norm == "SQL" and cand_norm in ["PostgreSQL", "MySQL", "SQLite"]:
            return True, "taxonomy_child"

        # e.g., Job requires "FastAPI" and candidate explicitly has "REST APIs"
        if cand_norm in TAXONOMY_TREE and job_norm in TAXONOMY_TREE[cand_norm]:
            return True, "taxonomy_parent"

        return False, "none"


skill_taxonomy = SkillTaxonomy()
