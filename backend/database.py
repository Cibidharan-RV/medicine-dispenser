import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

# Sync engine using the DATABASE_URL from env
engine = create_engine(settings.DATABASE_URL, echo=True, future=True)

# Session factory for sync sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """FastAPI dependency that provides a DB session and ensures proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
