# PLACEWISE — AI-Powered Adaptive Placement Preparation Agent

> **PLACEWISE** is an intelligent, closed-loop placement preparation system that analyzes a candidate's resume and target job description to compute deterministic skill gaps, generate targeted interview questions with a local LLM (`qwen3:4b`), grade candidate responses, update skill mastery, and adapt practice recommendations in real time.

---

##  Key Features

-  **Local Resume Parsing:** In-memory PDF text extraction using PyMuPDF (`fitz`).
-  **Local AI Inference:** Powered by Ollama and `qwen3:4b` with zero cloud API keys, zero cost, and 100% data privacy.
-  **Deterministic Skill Taxonomy:** Aliases and hierarchical normalization (`FastAPI` matches `REST APIs`, `PostgreSQL` matches `SQL`).
-  **Explainable Gap & Readiness Engine:** Transparent readiness formula ($70\%$ required, $30\%$ preferred weighting) and priority ranking.
-  **Adaptive Remediation Loop:** Immediately targets candidate mistakes and subtopic weaknesses.
-  **Mathematical Score Updates:** Formula-driven skill score progression: $\text{new\_score} = \text{round}(0.70 \times \text{prev} + 0.30 \times \text{ans})$.
-  **SQLite Persistence:** Session and attempt history survive application restarts.
-  **Modern React Dashboard:** Built with React 19, Vite, and Tailwind CSS.

---

##  Architecture & Separation of Concerns

```text
Resume PDF + Job Description
              ↓
  Candidate Profile & JD Analysis (Qwen3:4b)
              ↓
   Deterministic Skill Gap Engine (Taxonomy + Math)
              ↓
      Adaptive Planner (Remediation & Priority)
              ↓
  Targeted Interview Question (Qwen3:4b + Pydantic)
              ↓
       Candidate Answer
              ↓
     AI Answer Evaluation (0–100, Missing Concepts)
              ↓
Deterministic Skill State Update (0.7*prev + 0.3*ans)
              ↓
     Next Remediation Step
              ↓
           (Repeat)
```

### Is this just an LLM wrapper?
**No.** The LLM handles unstructured language tasks (resume parsing, question phrasing, answer feedback). Deterministic Python logic handles state persistence, skill normalization, priority calculation, score math, and adaptive loop control.

---

##  Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, Lucide React
- **Backend:** Python 3.12, FastAPI, Pydantic v2, PyMuPDF, SQLite
- **Local AI:** Ollama with `qwen3:4b`

---

##  Local Setup & Quickstart

### Prerequisites
- Windows 11 (or Linux/macOS)
- Python 3.12+
- Node.js v20+
- [Ollama](https://ollama.com/) with model `qwen3:4b` installed (`ollama pull qwen3:4b`)

---

### Step 1: Start Ollama
Ensure Ollama is running on your machine:
```bash
ollama serve
# Verify qwen3:4b is available
ollama list
```

---

### Step 2: Backend Setup
```powershell
# Navigate to project root
cd e:\Projects\Placewise

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend\requirements.txt

# Start FastAPI server
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload --port 8000
```
Backend API will be available at `http://localhost:8000` (API docs at `http://localhost:8000/docs`).

---

### Step 3: Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at `http://localhost:5173`.

---

##  Running Automated Tests

Run the complete test suite across health checks, resume parser, skill taxonomy, gap analyzer, adaptive planner, evaluator, and database CRUD:
```powershell
$env:PYTHONPATH="backend"
pytest backend/tests/test_health.py backend/tests/test_resume_parser.py backend/tests/test_gap_analyzer.py backend/tests/test_planner_and_evaluator.py backend/tests/test_api_endpoints.py -v
```

---

##  API Reference

- `POST /api/analyze`: Multi-part upload (PDF resume + target role + job description). Returns extracted profile, skill gaps, readiness score, and initial adaptive recommendation.
- `GET /api/candidate/{id}`: Returns candidate profile and current skill state.
- `GET /api/candidate/{id}/next-question`: Generates an adaptive question for the candidate's top priority gap or recent mistake.
- `POST /api/candidate/{id}/evaluate`: Evaluates candidate's answer, updates skill score in DB, and returns feedback + next recommendation.
- `GET /api/candidate/{id}/progress`: Returns candidate readiness, skill gaps, recent attempts, and current recommendation.
- `GET /health`: Health probe reporting server status and Ollama model availability.

---

##  Documentation Links
- [Solution Brief](docs/solution-brief.md)
- [System Architecture](docs/architecture.md)
- [Model Evaluation & Comparison](docs/model-comparison.md)
- [Failure Analysis & Post-Mortem](docs/failure-analysis.md)
