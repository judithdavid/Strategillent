from pathlib import Path

from pydantic import Field
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
    ollama_timeout_seconds: int = Field(default=120, ge=1, le=600)
    ollama_connect_timeout_seconds: int = Field(default=10, ge=1, le=120)
    ollama_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    ollama_num_ctx: int = Field(default=8192, ge=512, le=131072)
    ollama_num_predict: int = Field(default=2048, ge=1, le=32768)

    # Intelligence context limits
    intelligence_max_context_chars: int = Field(
        default=18000, ge=1000, le=100000
    )
    intelligence_max_evidence_records: int = Field(
        default=12, ge=1, le=100
    )
    intelligence_max_answer_chars: int = Field(
        default=12000, ge=500, le=50000
    )

    # LLM behaviour
    intelligence_use_llm: bool = True
    intelligence_allow_deterministic_fallback: bool = True

    # Retrieval
    qdrant_path: str = "../.qdrant/strategillent"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Online research
    tavily_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
