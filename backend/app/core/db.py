"""SQLAlchemy database session management.

Provides centralized database engine and session factory configuration.
Session lifecycle is managed through the get_session() FastAPI dependency.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _normalize_database_url(url: str) -> str:
    """Normalize database URL for psycopg3 driver compatibility.
    
    Converts postgres:// or plain postgresql:// URLs to postgresql+psycopg://
    following the same convention used in Alembic env.py.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def _create_engine() -> Engine:
    """Create and configure the SQLAlchemy engine.
    
    Returns:
        Configured SQLAlchemy Engine instance
    """
    db_url = _normalize_database_url(settings.DATABASE_URL)
    
    engine = create_engine(
        db_url,
        # Connection pool settings
        pool_size=5,
        max_overflow=10,
        pool_timeout=30.0,
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Verify connections before use
        # Echo SQL for debugging (disable in production)
        echo=False,
    )
    
    return engine


# Global engine instance - created once at module import
engine = _create_engine()


# Session factory - creates new sessions
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session.
    
    Creates a new session for each request, yields it to the endpoint,
    and ensures cleanup happens even if an exception occurs.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_session)):
            return db.query(Item).all()
    
    Yields:
        SQLAlchemy Session instance
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_engine() -> Engine:
    """Return the global engine instance.
    
    Useful for testing or advanced use cases that need direct engine access.
    
    Returns:
        SQLAlchemy Engine instance
    """
    return engine
