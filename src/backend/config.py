from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path to the directory containing this config.py file (src/backend)
CONFIG_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """
    Application settings are loaded from the .env file in the same directory.
    """

    DATABASE_URL: str

    # Load settings from the .env file located in the src/backend directory
    model_config = SettingsConfigDict(env_file=CONFIG_DIR / ".env")


# Create a single instance of the settings to be used throughout the application
settings = Settings()
