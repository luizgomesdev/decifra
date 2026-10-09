from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def repo_root(module_file: Path) -> Path:
    """Where `.env` and the reports folder live.

    In a checkout this file is at `apps/api/src/decifra/config.py`, four levels
    below the repository. In the container the package sits at `/app/src/decifra`
    and there is no repository above it.
    """
    parents = module_file.resolve().parents
    return parents[4] if len(parents) > 4 else parents[2]


REPO_ROOT = repo_root(Path(__file__))


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

    allowed_origins: str = "http://localhost:5173"

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
