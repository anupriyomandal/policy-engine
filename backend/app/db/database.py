from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings


# Railway provides DATABASE_URL
DATABASE_URL = settings.DATABASE_URL


# Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # avoids stale connections
    pool_recycle=300,        # prevents timeout issues
)


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for models
Base = declarative_base()


def init_db() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    Base.metadata.create_all(bind=engine)
