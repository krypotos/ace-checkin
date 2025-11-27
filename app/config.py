"""Application configuration"""
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://ace_user:ace_password@localhost:5432/ace_checkin"
    )
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

    class Config:
        env_file = ".env"


settings = Settings()
