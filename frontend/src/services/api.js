const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
  return res.json();
}

export async function analyzeProfile(formData) {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData, // FormData with resume, target_role, job_description
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis failed: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getCandidateProfile(candidateId) {
  const res = await fetch(`${API_BASE}/api/candidate/${candidateId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch profile: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getCandidateProgress(candidateId) {
  const res = await fetch(`${API_BASE}/api/candidate/${candidateId}/progress`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch progress: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getNextQuestion(candidateId) {
  const res = await fetch(`${API_BASE}/api/candidate/${candidateId}/next-question`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to generate question: HTTP ${res.status}`);
  }
  return res.json();
}

export async function evaluateAnswer(candidateId, questionId, answer) {
  const res = await fetch(`${API_BASE}/api/candidate/${candidateId}/evaluate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question_id: questionId,
      answer: answer,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Evaluation failed: HTTP ${res.status}`);
  }
  return res.json();
}
