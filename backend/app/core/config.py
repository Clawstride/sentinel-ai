"""
Application configuration.

Loads settings from environment variables (via a .env file in local
development) using pydantic-settings. This is the single source of
truth for configuration values across the app — no module should read
os.environ directly; everything goes through `settings`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General app settings
    APP_NAME: str = "SentinelAI"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # PostgreSQL settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def DATABASE_URL(self) -> str:
        """Builds the SQLAlchemy database URL from individual settings."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    lru_cache ensures the .env file is parsed only once and the same
    Settings object is reused across the app (acts like a singleton).
    """
    return Settings()


settings = get_settings()
