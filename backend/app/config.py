from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PLACEWISE"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    DATABASE_PATH: str = "placewise.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
