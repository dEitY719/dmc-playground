import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Path to the directory containing this config.py file (src/backend)
CONFIG_DIR = Path(__file__).resolve().parent


# src/backend/config.py


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(env_file=CONFIG_DIR / ".env", env_prefix="")

    @property
    def EFFECTIVE_DATABASE_URL(self) -> str:
        # pytest 실행 중이고 TEST_DATABASE_URL이 존재하면 그걸 사용
        if os.getenv("PYTEST_CURRENT_TEST") and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL


# Create a single instance of the settings to be used throughout the application
settings = Settings()
