# PLACEWISE — System Architecture & Engineering Design

## 1. Architectural Overview

PLACEWISE is designed as a hybrid deterministic-AI system. It avoids the common pitfall of being an "LLM wrapper" by cleanly separating probabilistic language comprehension from deterministic business logic, state management, and learning mathematics.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             REACT FRONTEND (Vite)                           │
│  - Setup Page (Resume PDF + JD)          - Adaptive Practice Page           │
│  - Interactive Dashboard (Gaps/Readiness)- Attempt History & Results        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            FASTAPI BACKEND LAYER                            │
│  /api/analyze  •  /api/candidate/{id}  •  /api/candidate/{id}/next-question  │
│  /api/candidate/{id}/evaluate          •  /api/candidate/{id}/progress      │
└───────────────┬─────────────────────────────────────────────┬───────────────┘
                │                                             │
┌───────────────▼────────────────┐           ┌────────────────▼───────────────┐
│     DETERMINISTIC ENGINE       │           │        AI INFERENCE LAYER      │
│  • PyMuPDF Resume Parser       │           │  • Centralized Ollama Client   │
│  • Skill Taxonomy & Aliases    │◄─────────►│  • Qwen3:4b Local Model        │
│  • Deterministic Gap Analyzer  │           │  • Structured Pydantic Parser  │
│  • 70/30 Readiness Math        │           │  • Reasoning Sanitizer (<think>)│
│  • Adaptive Learning Planner   │           └────────────────────────────────┘
│  • 0.7*prev + 0.3*ans Scoring  │
└───────────────┬────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────────────────┐
│                             SQLITE PERSISTENCE                              │
│  - candidates  •  jobs  •  skills  •  questions  •  question_attempts       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Responsibilities

### LLM Responsibilities (Language-Heavy)
- **Resume Understanding:** Extracting explicit technical tools, libraries, and project scopes from unstructured PDF text.
- **Job Description Extraction:** Identifying required vs preferred technical competencies.
- **Question Synthesis:** Formulating scenario-based, conceptual questions on targeted subtopics.
- **Answer Evaluation:** Grading technical correctness (0–100), identifying missing concepts or edge cases, and generating constructive feedback.

### Application Logic Responsibilities (Deterministic)
- **Skill Normalization:** Standardizing aliases (`postgres` $\to$ `PostgreSQL`, `sklearn` $\to$ `scikit-learn`).
- **Hierarchical Taxonomy Matching:** Recognizing that child implementations satisfy broad category requirements (`FastAPI` matches `REST APIs`) while rejecting irrelevant skills (`MongoDB` on resume when JD only asks for SQL).
- **Initial Baseline Scoring:** Assigning explainable initial baselines ($80\%$ for skills with projects, $72\%$ for skills list, $65\%$ for taxonomy match, $0\%$ for missing).
- **Job Readiness Calculation:** Weighted mathematical formula ($70\%$ required, $30\%$ preferred).
- **Skill Score Updating:** Updating skill state using $\text{new\_score} = \text{round}(0.70 \times \text{prev} + 0.30 \times \text{ans})$.
- **Adaptive Planning & Remediation:** Recommending subtopics and triggering remediation when recent scores drop below $65\%$.
- **Data Persistence:** Maintaining candidate progress across restarts in SQLite.

---

## 3. Database Schema

```sql
-- Candidate profile
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    target_role TEXT NOT NULL,
    resume_text TEXT NOT NULL,
    projects_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Target job description & extracted requirements
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    target_role TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills_json TEXT NOT NULL DEFAULT '[]',
    preferred_skills_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
);

-- Candidate skill proficiency state
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    required INTEGER NOT NULL DEFAULT 0,
    preferred INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'resume',
    matched INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE,
    UNIQUE(candidate_id, skill_name)
);

-- Adaptive questions generated
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    skill TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
);

-- Question attempts & evaluations
CREATE TABLE question_attempts (
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
);
```

---

## 4. API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/analyze` | Accepts PDF resume upload + target role + JD, extracts entities, computes gaps, saves state, returns initial analysis. |
| `GET` | `/api/candidate/{id}` | Returns candidate profile and current skill state. |
| `GET` | `/api/candidate/{id}/next-question` | Adaptive planner computes weakest gap / remediation and generates targeted interview question. |
| `POST` | `/api/candidate/{id}/evaluate` | Evaluates answer, updates skill score in DB via formula, saves attempt, returns feedback & next recommendation. |
| `GET` | `/api/candidate/{id}/progress` | Returns updated readiness, skill breakdown, attempt history, and current focus recommendation. |
| `GET` | `/health` | Real-time health check verifying FastAPI server and Ollama daemon connectivity. |
