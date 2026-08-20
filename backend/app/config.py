# app/config.py
# Centralised settings loaded from .env via pydantic-settings.
# Every module should import `settings` from here — never read os.environ directly.

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# __file__ = tau-park-project/backend/app/config.py
# .parent      → tau-park-project/backend/app/
# .parent.parent   → tau-park-project/backend/
# .parent.parent.parent → tau-park-project/   ← root, where .env lives
_ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────────────────────
    # asyncpg-compatible URL, e.g. postgresql+asyncpg://user:pass@host/db
    DATABASE_URL: str

    # ── JWT ─────────────────────────────────────────────────────────────────
    SECRET_KEY: str                          # Long random string, keep secret!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ── App Meta ─────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "TAU-PARK API"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",          # Ignore Prisma-specific vars like DATABASE_URL format
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS_ORIGINS as a parsed list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Singleton instance used across the entire application
settings = Settings()
