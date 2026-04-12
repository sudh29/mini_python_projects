"""
Application configuration — loaded from environment variables.
Uses pydantic-settings for type-safe, validated config.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Jorie AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────────
    # SQLite for prototyping; swap to postgresql+asyncpg:// for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./rpa_platform.db"

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CHANNEL_STATUS: str = "rpa:status_updates"

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── Auth ─────────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    ALGORITHM: str = "HS256"

    # ── Artifact Storage ─────────────────────────────────────────
    ARTIFACT_STORAGE_PATH: Path = Path("./artifacts")

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Next.js fallback
    ]

    @property
    def artifact_base(self) -> Path:
        self.ARTIFACT_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        return self.ARTIFACT_STORAGE_PATH


settings = Settings()
