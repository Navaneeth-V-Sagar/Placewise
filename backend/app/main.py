from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from app.config import settings
from app.api.analysis import router as analysis_router
from app.api.candidate import router as candidate_router
from app.api.assessment import router as assessment_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PLACEWISE — AI-Powered Adaptive Placement Preparation Agent"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(candidate_router, prefix=settings.API_V1_STR)
app.include_router(assessment_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    ollama_status = "unreachable"
    models_available = []
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models_available = [m.get("name") for m in data.get("models", [])]
                ollama_status = "ready" if any(settings.OLLAMA_MODEL in m for m in models_available) else "model_missing"
    except Exception as e:
        ollama_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ollama": {
            "status": ollama_status,
            "host": settings.OLLAMA_HOST,
            "configured_model": settings.OLLAMA_MODEL,
            "models_available": models_available
        }
    }
