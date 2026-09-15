import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration loaded from environment variables or a .env file."""

    DATABASE_URL: str = Field(..., description="SQLAlchemy DB URL, e.g., postgresql://user:pwd@host/db")
    SECRET_KEY: SecretStr = Field(..., description="Secret key for signing JWT tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, description="Expiration time for access tokens (minutes)")
    HARDWARE_API_KEY: SecretStr = Field(..., description="API Key for ESP32 hardware endpoints")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

# Global settings instance
settings = Settings()
