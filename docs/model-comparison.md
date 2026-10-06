# Model Evaluation & Selection for PLACEWISE

## 1. Context & Objective
Before building PLACEWISE, a local model evaluation was conducted to select the most reliable, cost-effective, and schema-compliant local LLM for our six target workloads.

The requirements for model selection were:
1. **Fully local inference** via Ollama on consumer hardware (no cloud API keys, zero inference cost, complete candidate privacy).
2. **Strict JSON schema adherence** when parsed with Pydantic.
3. **High technical fidelity** in extracting programming concepts and grading technical interview responses.

---

## 2. Evaluation Methodology & Workloads
Two candidate local models were evaluated across six distinct PLACEWISE workloads:

1. **Resume Extraction:** Identifying explicit programming languages, frameworks, and project scopes without hallucinating non-existent skills.
2. **Job Description Extraction:** Accurately classifying mandatory (`required`) vs nice-to-have (`preferred`) technical requirements.
3. **Skill-Gap Analysis:** Correctly distinguishing matched vs missing competencies against a target role.
4. **Question Generation:** Generating conceptual, scenario-based interview questions rather than rote definitions.
5. **Answer Evaluation:** Grading candidate answers, isolating missed edge cases, and outputting structured feedback.
6. **Adaptive Planning Guidance:** Proposing relevant subtopics based on candidate performance.

---

## 3. Observed Results Across Workloads

| Workload | Candidate Model A | Qwen3:4b (Selected) | Observed Distinction |
|---|---|---|---|
| **1. Resume Extraction** | High recall, but occasionally hallucinated implied libraries (e.g. adding NumPy when only Python was mentioned). | High precision; extracted only explicitly stated tools and projects. | Qwen3 strictly adhered to negative constraints ("do not invent skills"). |
| **2. JD Extraction** | Mixed required and preferred skills into a single flat list. | Successfully separated `required_skills` from `preferred_skills`. | Qwen3 showed superior sensitivity to modal verbs ("must have" vs "is a plus"). |
| **3. Skill-Gap Linguistic Mapping** | Produced verbose text explanations rather than clean structured mapping. | Extracted clean entity names easily parsed by deterministic taxonomy rules. | Qwen3 outputs were cleaner for Pydantic validation. |
| **4. Question Generation** | Tended toward generic trivia questions (e.g., *"What is SQL?"*). | Generated practical scenarios (e.g., *"Explain how a LEFT JOIN handles non-matching rows and where NULL values appear"*). | Qwen3 generated higher-depth technical interview prompts. |
| **5. Answer Evaluation** | Scores clustered around 70–80 regardless of answer quality; missed subtle edge cases. | Accurately differentiated partial correctness and listed specific missing concepts. | Qwen3 provided more actionable and granular missing concepts. |
| **6. Adaptive Planning Guidance** | Recommended broad generic topics (e.g., *"Practice Databases"*). | Recommended granular subtopics (e.g., *"LEFT JOIN & NULL Handling"*). | Qwen3 aligned well with hierarchical subtopic taxonomies. |

---

## 4. Selection Conclusion & Engineering Takeaway

### Selected Model: `qwen3:4b`

> **Note on Model Scope:**
> We do not claim that Qwen3:4b is universally superior to all models in all domains. 
> The accurate finding is: **Qwen3:4b performed better on the specific workloads and schema constraints evaluated for PLACEWISE.**

### Key Architectural Decision:
While Qwen3:4b proved effective for linguistic extraction and evaluation, we decided **never to let the LLM execute numerical calculations, readiness formulas, or state persistence directly**. Instead, Qwen3:4b serves as the language intelligence layer, while deterministic Python algorithms control skill state, gap rankings, and learning formulas.
