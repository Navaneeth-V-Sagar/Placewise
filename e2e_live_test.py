import pymupdf
import json
import time
from fastapi.testclient import TestClient
from app.main import app

def create_sample_resume_pdf():
    doc = pymupdf.open()
    page = doc.new_page()
    content = """Alex Rivera
Software Engineer & AI Practitioner

Technical Skills:
Python, FastAPI, Docker, Git, JavaScript

Experience & Projects:
- E-Commerce REST Microservices: Designed scalable endpoints with FastAPI and Redis caching.
- Data Analytics Pipeline: Automated data ingestion with Python and Dockerized container workflows.
"""
    page.insert_text((50, 72), content, fontsize=11)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def main():
    print("=" * 60)
    print("PLACEWISE - COMPLETE END-TO-END VERIFICATION")
    print("=" * 60)

    client = TestClient(app)

    # 1. Health check
    print("\n[Step 1] Checking Backend & Ollama Health...")
    resp = client.get("/health")
    print("Health Status Code:", resp.status_code)
    health = resp.json()
    print("Health Response:", json.dumps(health, indent=2))
    assert resp.status_code == 200
    assert health["ollama"]["status"] == "ready"

    # 2. Profile Analysis
    print("\n[Step 2] Submitting Profile Analysis (Resume PDF + Target Role + JD)...")
    pdf_bytes = create_sample_resume_pdf()
    
    target_role = "AI Backend Engineer"
    job_description = """We are hiring an AI Backend Engineer.
Requirements:
- Strong Python & REST APIs (FastAPI preferred).
- Deep experience in SQL (PostgreSQL query optimization, JOINs, aggregation).
- Understanding of Machine Learning fundamentals.
Preferred:
- Docker containerization and Git version control."""

    files = {
        "resume": ("Alex_Rivera_Resume.pdf", pdf_bytes, "application/pdf")
    }
    data = {
        "target_role": target_role,
        "job_description": job_description
    }

    t0 = time.time()
    resp = client.post("/api/analyze", files=files, data=data)
    t1 = time.time()
    print(f"Analysis completed in {t1-t0:.2f}s, Status Code: {resp.status_code}")
    if resp.status_code != 201:
        print("Error detail:", resp.text)
        assert resp.status_code == 201

    analysis = resp.json()
    candidate_id = analysis["candidate_id"]
    print(f"Candidate Created: ID #{candidate_id} ({analysis['candidate_name']})")
    print(f"Extracted Skills: {analysis['extracted_skills']}")
    print(f"Matched Skills: {analysis['matched_skills']}")
    print(f"Readiness Score: {analysis['readiness']}%")
    print("Skill Gaps:")
    for gap in analysis["skill_gaps"]:
        print(f"  - {gap['skill_name']} (Score: {gap['score']}%, Priority {gap['priority']}, {gap['importance']})")
    print("Recommended Focus:", analysis["recommended_focus"])

    # 3. Next Adaptive Question
    print("\n[Step 3] Fetching Next Adaptive Question...")
    t0 = time.time()
    resp = client.get(f"/api/candidate/{candidate_id}/next-question")
    t1 = time.time()
    print(f"Question generated in {t1-t0:.2f}s, Status Code: {resp.status_code}")
    assert resp.status_code == 200
    q_data = resp.json()
    question_id = q_data["question_id"]
    print(f"Question #{question_id} for Skill: {q_data['skill']}, Topic: {q_data['topic']} ({q_data['difficulty']})")
    print(f"Question Text: {q_data['question']}")

    # 4. Evaluate Answer
    print("\n[Step 4] Submitting Candidate Answer for Evaluation...")
    candidate_answer = "A LEFT JOIN returns all rows from the left table and matching rows from the right table. If there is no match, the columns from the right table will contain NULL values. We can filter for unmatched rows using WHERE right_table.id IS NULL."
    
    t0 = time.time()
    resp = client.post(
        f"/api/candidate/{candidate_id}/evaluate",
        json={"question_id": question_id, "answer": candidate_answer}
    )
    t1 = time.time()
    print(f"Evaluation completed in {t1-t0:.2f}s, Status Code: {resp.status_code}")
    assert resp.status_code == 200
    eval_data = resp.json()
    print(f"Score Awarded: {eval_data['score']}/100 ({eval_data['correctness']})")
    print(f"Skill Score Transition: {eval_data['previous_skill_score']}% -> {eval_data['new_skill_score']}%")
    print(f"Feedback: {eval_data['feedback']}")
    print("Missing Concepts:", eval_data["missing_concepts"])
    print("Next Adaptive Recommendation:", eval_data["next_recommendation"])

    # 5. Progress Tracking
    print("\n[Step 5] Checking Progress & Attempt History...")
    resp = client.get(f"/api/candidate/{candidate_id}/progress")
    assert resp.status_code == 200
    progress = resp.json()
    print(f"Updated Job Readiness: {progress['readiness']}%")
    print(f"Total Attempts Logged: {len(progress['recent_attempts'])}")
    print(f"Next Focus Topic: {progress['current_recommendation']['recommended_topic']}")

    print("\n" + "=" * 60)
    print("ALL LIVE END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
