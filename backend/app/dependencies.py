from typing import Generator
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.config import settings


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session per request.
    Automatically closes after request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings():
    """
    Dependency to access app settings.
    """
    return settings