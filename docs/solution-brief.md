# PLACEWISE — Solution Brief

## 1. Executive Summary & User Problem
Placement preparation for engineering students is traditionally broken, generic, and unguided:
- Students practice randomly from massive 500+ question banks with zero personalization.
- Candidates lack objective awareness of their exact skill gaps relative to target job postings.
- Crucial prerequisite gaps (e.g., struggling with `NULL` handling in SQL `LEFT JOIN`s or idempotency in REST APIs) remain unaddressed.
- Candidates receive subjective, delayed, or superficial feedback without concrete remediation.

**PLACEWISE** solves this by providing an **AI-powered adaptive placement preparation agent** that makes preparation strictly **candidate-specific and job-specific**.

---

## 2. Target User
- **Primary User:** Final-year / pre-final-year college engineering students preparing for Software Engineering, Full-Stack, Backend, and AI/ML placement interviews.
- **Context:** Single-candidate local interview preparation agent.

---

## 3. Product Goal & Proposed Solution
The core goal of PLACEWISE is to close the candidate's specific job readiness gap through a closed-loop adaptive cycle:

```text
Resume PDF + Job Description
              ↓
  Candidate Profile & JD Analysis
              ↓
   Deterministic Skill Gap Engine
              ↓
      Adaptive Planner
              ↓
  Targeted Interview Question
              ↓
       Candidate Answer
              ↓
     AI Answer Evaluation
              ↓
Deterministic Skill State Update
              ↓
     Next Remediation Step
              ↓
           (Repeat)
```

Instead of:
> *"Here are 100 random SQL questions."*

PLACEWISE determines:
> *"Your target AI Engineer role requires SQL. You demonstrated Python and FastAPI on your resume, but SQL is missing. Your latest attempt on `LEFT JOIN` struggled with NULL handling. Practice this specific scenario next."*

---

## 4. MVP Scope & Boundaries
- **Included Core Features:**
  - PyMuPDF-powered local resume text extraction.
  - Qwen3:4b LLM linguistic entity extraction and answer evaluation.
  - Deterministic skill taxonomy, canonical normalization, and relationship matching.
  - Transparent readiness formula ($70\%$ required, $30\%$ preferred weighting).
  - Adaptive remediation planner that responds to recent attempt mistakes.
  - Deterministic skill state updates: $\text{new\_score} = \text{round}(0.70 \times \text{prev} + 0.30 \times \text{ans})$.
  - SQLite persistence for candidate sessions, skill baselines, questions, and attempt history.
  - Modern React + Vite + Tailwind CSS dashboard.
- **Explicit Non-Goals (Out of Scope):**
  - Authentication, multi-tenancy, payments, cloud databases, voice/video streaming, or external API keys.

---

## 5. Success Criteria
1. **End-to-End Functionality:** Complete loop functions without hangs or crashes.
2. **Reliable Local AI Integration:** Qwen3:4b parses resumes, job descriptions, generates targeted questions, and grades responses into schema-validated Pydantic models.
3. **Architectural Separation:** LLM handles language; deterministic Python handles state, score math, priority calculations, and progression.
4. **Explainable Engineering:** Every number, readiness percentage, and recommendation is deterministic and defensible.
