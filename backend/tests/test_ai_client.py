import time
import pytest
from app.ai.client import (
    ai_client,
    OllamaClient,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaValidationError
)
from app.schemas import ResumeAnalysis


def test_clean_json_text_unit():
    """Unit test: Verify stripping of <think>...</think> reasoning tokens and markdown codeblocks."""
    raw = "<think>Analyzing candidate experience and skills...</think>```json\n{\"technical_skills\": [\"Python\", \"FastAPI\"], \"projects\": [\"API Gateway\"]}\n```"
    cleaned = OllamaClient.clean_json_text(raw)
    assert "<think>" not in cleaned
    assert "```" not in cleaned
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")


@pytest.mark.anyio
async def test_ollama_connection_error_handling():
    """Unit test: Verify that an unreachable host raises OllamaConnectionError or OllamaTimeoutError cleanly."""
    bad_client = OllamaClient(host="http://127.0.0.1:59999", timeout=1.0)
    with pytest.raises((OllamaConnectionError, OllamaTimeoutError)):
        await bad_client.generate_structured(
            prompt="Extract skills from text",
            response_model=ResumeAnalysis
        )


@pytest.mark.anyio
async def test_ollama_structured_generation_minimal():
    """
    Live integration test against Ollama HTTP API (http://localhost:11434) with qwen3:4b.
    Verifies structured Pydantic output validation and measures actual response time.
    """
    prompt = "Extract technical skills and projects from: 2 years experience with Python, FastAPI, and PostgreSQL. Built a Realtime Analytics Dashboard."
    
    start_time = time.perf_counter()
    result = await ai_client.generate_structured(
        prompt=prompt,
        response_model=ResumeAnalysis,
        system_prompt="Extract technical skills and projects."
    )
    elapsed = time.perf_counter() - start_time
    
    print(f"\n[AI Integration Test] Response time: {elapsed:.2f}s")
    print(f"[AI Integration Test] Extracted skills: {result.technical_skills}")
    print(f"[AI Integration Test] Extracted projects: {result.projects}")
    
    assert isinstance(result, ResumeAnalysis)
    assert len(result.technical_skills) > 0
    skills_lower = [s.lower() for s in result.technical_skills]
    assert any("python" in s for s in skills_lower)
    assert isinstance(result.projects, list)
