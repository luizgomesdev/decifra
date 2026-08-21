from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    openai_api_key: str
    openai_reasoning_model: str = "gpt-5.6-terra"
    openai_fast_model: str = "gpt-5.6-luna"
    openai_embedding_model: str = "text-embedding-3-small"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "genetic_reports"

    database_url: str = "postgresql+psycopg://decifra:decifra@localhost:5433/decifra"

    reports_dir: Path = REPO_ROOT / "data" / "reports"


@lru_cache
def get_settings() -> Settings:
    return Settings()
