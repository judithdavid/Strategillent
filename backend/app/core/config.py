from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Strategillent/
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    app_name: str = "Strategillent"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = "sqlite:///./strategillent.db"

    # Local LLM configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Online research configuration
    tavily_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()