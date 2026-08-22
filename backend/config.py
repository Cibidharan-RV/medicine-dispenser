import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration loaded from environment variables or a .env file."""

    DATABASE_URL: str = Field(..., env="DATABASE_URL", description="SQLAlchemy DB URL, e.g., postgresql://user:pwd@host/db")
    SECRET_KEY: SecretStr = Field(..., env="SECRET_KEY", description="Secret key for signing JWT tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES", description="Expiration time for access tokens (minutes)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
