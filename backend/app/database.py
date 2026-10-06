import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.schemas import (
    SkillItem,
    GapItem,
    Question,
    Evaluation,
    QuestionAttemptItem,
    PlannerRecommendation
)


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes the database schema with required tables and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Candidates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target_role TEXT NOT NULL,
                    resume_text TEXT NOT NULL,
                    projects_json TEXT NOT NULL DEFAULT '[]',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER NOT NULL,
                    target_role TEXT NOT NULL,
                    description TEXT NOT NULL,
                    required_skills_json TEXT NOT NULL DEFAULT '[]',
                    preferred_skills_json TEXT NOT NULL DEFAULT '[]',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
                )
            """)

            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER NOT NULL,
                    skill_name TEXT NOT NULL,
                    score INTEGER NOT NULL DEFAULT 0,
                    required INTEGER NOT NULL DEFAULT 0,
                    preferred INTEGER NOT NULL DEFAULT 0,
                    source TEXT NOT NULL DEFAULT 'resume',
                    matched INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE,
                    UNIQUE(candidate_id, skill_name)
                )
            """)

            # Questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER NOT NULL,
                    skill TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    question TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
                )
            """)

            # Question attempts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS question_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    candidate_id INTEGER NOT NULL,
                    skill TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    correctness TEXT NOT NULL,
                    missing_concepts_json TEXT NOT NULL DEFAULT '[]',
                    feedback TEXT NOT NULL,
                    recommended_next_topic TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    # --- Candidate Operations ---
    def create_candidate(self, name: str, target_role: str, resume_text: str, projects: List[str]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO candidates (name, target_role, resume_text, projects_json) VALUES (?, ?, ?, ?)",
                (name, target_role, resume_text, json.dumps(projects))
            )
            conn.commit()
            return cursor.lastrowid

    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "name": row["name"],
                "target_role": row["target_role"],
                "resume_text": row["resume_text"],
                "projects": json.loads(row["projects_json"]),
                "created_at": row["created_at"]
            }

    # --- Job Operations ---
    def create_job(self, candidate_id: int, target_role: str, description: str, required_skills: List[str], preferred_skills: List[str]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO jobs (candidate_id, target_role, description, required_skills_json, preferred_skills_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (candidate_id, target_role, description, json.dumps(required_skills), json.dumps(preferred_skills))
            )
            conn.commit()
            return cursor.lastrowid

    def get_job_by_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE candidate_id = ? ORDER BY id DESC LIMIT 1", (candidate_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "candidate_id": row["candidate_id"],
                "target_role": row["target_role"],
                "description": row["description"],
                "required_skills": json.loads(row["required_skills_json"]),
                "preferred_skills": json.loads(row["preferred_skills_json"]),
                "created_at": row["created_at"]
            }

    # --- Skills Operations ---
    def save_skills(self, candidate_id: int, skills: List[SkillItem]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for s in skills:
                cursor.execute(
                    """INSERT INTO skills (candidate_id, skill_name, score, required, preferred, source, matched)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(candidate_id, skill_name) DO UPDATE SET
                           score=excluded.score,
                           required=excluded.required,
                           preferred=excluded.preferred,
                           source=excluded.source,
                           matched=excluded.matched""",
                    (candidate_id, s.skill_name, s.score, 1 if s.required else 0, 1 if s.preferred else 0, s.source, 1 if s.matched else 0)
                )
            conn.commit()

    def get_candidate_skills(self, candidate_id: int) -> List[SkillItem]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE candidate_id = ? ORDER BY score DESC, skill_name ASC", (candidate_id,))
            rows = cursor.fetchall()
            skills = []
            for r in rows:
                score = r["score"]
                status = "strong" if score >= 70 else ("moderate" if score >= 50 else "gap")
                skills.append(SkillItem(
                    id=r["id"],
                    skill_name=r["skill_name"],
                    score=score,
                    required=bool(r["required"]),
                    preferred=bool(r["preferred"]),
                    source=r["source"],
                    matched=bool(r["matched"]),
                    status=status
                ))
            return skills

    def update_skill_score(self, candidate_id: int, skill_name: str, new_score: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE skills SET score = ? WHERE candidate_id = ? AND skill_name = ?",
                (new_score, candidate_id, skill_name)
            )
            # If skill did not exist, insert it
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO skills (candidate_id, skill_name, score, source, matched) VALUES (?, ?, ?, 'practice', 1)",
                    (candidate_id, skill_name, new_score)
                )
            conn.commit()

    # --- Questions & Attempts ---
    def save_question(self, candidate_id: int, question: Question) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO questions (candidate_id, skill, topic, difficulty, question)
                   VALUES (?, ?, ?, ?, ?)""",
                (candidate_id, question.skill, question.topic, question.difficulty, question.question)
            )
            conn.commit()
            return cursor.lastrowid

    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "candidate_id": row["candidate_id"],
                "skill": row["skill"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "question": row["question"],
                "created_at": row["created_at"]
            }

    def save_attempt(
        self,
        question_id: int,
        candidate_id: int,
        skill: str,
        topic: str,
        difficulty: str,
        question: str,
        answer: str,
        evaluation: Evaluation
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO question_attempts
                   (question_id, candidate_id, skill, topic, difficulty, question, answer, score, correctness, missing_concepts_json, feedback, recommended_next_topic)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    question_id,
                    candidate_id,
                    skill,
                    topic,
                    difficulty,
                    question,
                    answer,
                    evaluation.score,
                    evaluation.correctness,
                    json.dumps(evaluation.missing_concepts),
                    evaluation.feedback,
                    evaluation.recommended_next_topic
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_candidate_attempts(self, candidate_id: int, limit: int = 10) -> List[QuestionAttemptItem]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM question_attempts WHERE candidate_id = ? ORDER BY id DESC LIMIT ?",
                (candidate_id, limit)
            )
            rows = cursor.fetchall()
            attempts = []
            for r in rows:
                attempts.append(QuestionAttemptItem(
                    id=r["id"],
                    skill=r["skill"],
                    topic=r["topic"],
                    difficulty=r["difficulty"],
                    question=r["question"],
                    answer=r["answer"],
                    score=r["score"],
                    correctness=r["correctness"],
                    missing_concepts=json.loads(r["missing_concepts_json"]),
                    feedback=r["feedback"],
                    recommended_next_topic=r["recommended_next_topic"],
                    created_at=datetime.fromisoformat(r["created_at"]) if isinstance(r["created_at"], str) else r["created_at"]
                ))
            return attempts


# Singleton database instance
db = Database()
