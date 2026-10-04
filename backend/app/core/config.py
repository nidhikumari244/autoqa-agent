import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoQA Engine"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/autoqa.db"
    
    # LLM Settings (Defaults to Gemini, supports OpenAI/Groq)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    
    # Browser Settings
    HEADLESS: bool = True
    BROWSER_VIEWPORT_WIDTH: int = 1280
    BROWSER_VIEWPORT_HEIGHT: int = 800
    ACTION_TIMEOUT_MS: int = 15000
    MAX_STEPS_PER_RUN: int = 30
    
    # Artifacts
    ARTIFACTS_PATH: Path = ARTIFACTS_DIR

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
