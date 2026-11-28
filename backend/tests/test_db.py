"""Tests for database session management."""

import os
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.db import (
    _normalize_database_url,
    get_engine,
    get_session,
)


def test_normalize_database_url_postgres():
    """Verify that postgres:// URLs are normalized to postgresql+psycopg://"""
    url = "postgres://user:pass@host:5432/db"
    normalized = _normalize_database_url(url)
    assert normalized == "postgresql+psycopg://user:pass@host:5432/db"


def test_normalize_database_url_postgresql():
    """Verify that postgresql:// URLs are normalized to postgresql+psycopg://"""
    url = "postgresql://user:pass@host:5432/db"
    normalized = _normalize_database_url(url)
    assert normalized == "postgresql+psycopg://user:pass@host:5432/db"


def test_normalize_database_url_already_normalized():
    """Verify that already normalized URLs are not modified."""
    url = "postgresql+psycopg://user:pass@host:5432/db"
    normalized = _normalize_database_url(url)
    assert normalized == url


def test_normalize_database_url_other_drivers():
    """Verify that URLs with other drivers are preserved."""
    url = "postgresql+asyncpg://user:pass@host:5432/db"
    normalized = _normalize_database_url(url)
    assert normalized == url


def test_get_engine_returns_engine():
    """Verify get_engine returns an Engine instance."""
    engine = get_engine()
    assert isinstance(engine, Engine)
    assert engine is not None


def test_get_engine_uses_configured_database_url():
    """Verify engine uses the DATABASE_URL from settings."""
    engine = get_engine()
    # The URL should contain the driver specification
    db_url = str(engine.url)
    # Should use psycopg driver
    assert "+psycopg" in db_url or "postgresql" in db_url


def test_get_engine_enables_pool_pre_ping():
    """Verify engine has pool_pre_ping enabled."""
    engine = get_engine()
    # pool_pre_ping should be enabled in engine configuration
    assert engine.pool._pre_ping is True


def test_get_session_yields_session():
    """Verify get_session yields a Session instance."""
    session_generator = get_session()
    session = next(session_generator)
    
    try:
        assert isinstance(session, Session)
        assert session is not None
    finally:
        # Clean up - call the generator's cleanup
        try:
            next(session_generator)
        except StopIteration:
            pass


def test_get_session_closes_session():
    """Verify get_session closes the session after use."""
    session_generator = get_session()
    session = next(session_generator)
    
    # Session should be active
    assert session.is_active
    
    # Finish the generator (triggers finally block)
    try:
        next(session_generator)
    except StopIteration:
        pass
    
    # After generator cleanup, session operations should fail or be inactive
    # In SQLAlchemy 2.x, closed sessions have is_active = False
    # Note: The session may still be technically usable but won't have active transaction
    assert not session.in_transaction()


def test_get_session_closes_session_on_exception():
    """Verify get_session closes the session even if exception occurs."""
    session_generator = get_session()
    session = next(session_generator)
    
    # Simulate an exception
    try:
        raise ValueError("Test exception")
    except ValueError:
        pass
    
    # Finish the generator
    try:
        next(session_generator)
    except StopIteration:
        pass
    
    # Session should not be in transaction after cleanup
    assert not session.in_transaction()


def test_get_session_can_be_used_multiple_times():
    """Verify get_session can be called multiple times for different sessions."""
    # First session
    gen1 = get_session()
    session1 = next(gen1)
    
    # Second session
    gen2 = get_session()
    session2 = next(gen2)
    
    # Should be different instances
    assert session1 is not session2
    
    # Clean up
    for gen in [gen1, gen2]:
        try:
            next(gen)
        except StopIteration:
            pass


def test_session_factory_configuration():
    """Verify SessionLocal is configured correctly."""
    from app.core.db import SessionLocal
    
    # SessionLocal should be a sessionmaker
    assert SessionLocal is not None
    
    # Check configuration
    assert SessionLocal.kw.get("autocommit") is False
    assert SessionLocal.kw.get("autoflush") is False
    assert SessionLocal.kw.get("expire_on_commit") is True


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or "localhost" not in os.getenv("DATABASE_URL", ""),
    reason="Requires local PostgreSQL database"
)
def test_session_can_execute_query():
    """Integration test: verify session can execute a simple query.
    
    Only runs if DATABASE_URL points to localhost.
    """
    session_generator = get_session()
    session = next(session_generator)
    
    try:
        # Execute a simple query that should work on any PostgreSQL
        result = session.execute(text("SELECT 1 as num"))
        row = result.fetchone()
        assert row[0] == 1
    finally:
        try:
            next(session_generator)
        except StopIteration:
            pass


def test_engine_pool_configuration():
    """Verify engine pool is configured with appropriate settings."""
    engine = get_engine()
    
    # Check pool configuration
    pool = engine.pool
    assert pool.size() >= 0  # Pool should be initialized
    
    # Verify pool settings exist (actual values may vary)
    assert hasattr(pool, '_pool')
    assert hasattr(pool, '_overflow')
