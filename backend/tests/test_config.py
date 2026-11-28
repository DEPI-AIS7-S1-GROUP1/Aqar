"""Tests for centralized settings configuration."""

import os
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_loads_defaults():
    """Verify that Settings loads with default values."""
    # Clear environment to ensure we get defaults
    env_backup = {}
    test_keys = [
        "DATABASE_URL", "REDIS_URL", "JWT_SECRET", "CORS_ORIGINS",
        "USE_REAL_LISTINGS", "USE_REAL_FINANCE", "USE_REAL_RAG",
        "USE_REAL_CONVERSATIONS", "USE_REAL_LEADS", "USE_REAL_AGENT"
    ]
    for key in test_keys:
        if key in os.environ:
            env_backup[key] = os.environ.pop(key)
    
    try:
        settings = Settings()
        
        # Check defaults
        assert "postgresql://" in settings.DATABASE_URL
        assert "redis://" in settings.REDIS_URL
        assert settings.CORS_ORIGINS == "http://localhost:3000"
        assert settings.cors_origins_list == ["http://localhost:3000"]
        
        # Feature flags default to False
        assert settings.USE_REAL_LISTINGS is False
        assert settings.USE_REAL_FINANCE is False
        assert settings.USE_REAL_RAG is False
        assert settings.USE_REAL_CONVERSATIONS is False
        assert settings.USE_REAL_LEADS is False
        assert settings.USE_REAL_AGENT is False
    finally:
        # Restore environment
        os.environ.update(env_backup)


def test_settings_loads_from_environment():
    """Verify that Settings loads from environment variables."""
    # Set test environment variables
    os.environ["DATABASE_URL"] = "postgresql://test:test@testhost:5432/testdb"
    os.environ["REDIS_URL"] = "redis://testhost:6379/1"
    os.environ["JWT_SECRET"] = "test-secret-key"
    os.environ["CORS_ORIGINS"] = "http://localhost:3000,https://example.com"
    os.environ["USE_REAL_LISTINGS"] = "true"
    os.environ["USE_REAL_FINANCE"] = "1"
    
    try:
        settings = Settings()
        
        assert settings.DATABASE_URL == "postgresql://test:test@testhost:5432/testdb"
        assert settings.REDIS_URL == "redis://testhost:6379/1"
        assert settings.JWT_SECRET == "test-secret-key"
        assert settings.CORS_ORIGINS == "http://localhost:3000,https://example.com"
        assert settings.cors_origins_list == ["http://localhost:3000", "https://example.com"]
        assert settings.USE_REAL_LISTINGS is True
        assert settings.USE_REAL_FINANCE is True
        assert settings.USE_REAL_RAG is False  # Not set, should be False
    finally:
        # Clean up test environment
        for key in ["DATABASE_URL", "REDIS_URL", "JWT_SECRET", "CORS_ORIGINS", 
                    "USE_REAL_LISTINGS", "USE_REAL_FINANCE"]:
            os.environ.pop(key, None)


def test_cors_origins_parses_string():
    """Verify CORS_ORIGINS correctly parses comma-separated string."""
    os.environ["CORS_ORIGINS"] = "http://localhost:3000,https://example.com,https://app.example.com"
    
    try:
        settings = Settings()
        assert settings.cors_origins_list == [
            "http://localhost:3000",
            "https://example.com",
            "https://app.example.com"
        ]
    finally:
        os.environ.pop("CORS_ORIGINS", None)


def test_cors_origins_handles_whitespace():
    """Verify CORS_ORIGINS handles whitespace in comma-separated values."""
    os.environ["CORS_ORIGINS"] = "http://localhost:3000 , https://example.com ,  https://app.example.com  "
    
    try:
        settings = Settings()
        assert settings.cors_origins_list == [
            "http://localhost:3000",
            "https://example.com",
            "https://app.example.com"
        ]
    finally:
        os.environ.pop("CORS_ORIGINS", None)


def test_feature_flags_accept_various_boolean_formats():
    """Verify feature flags accept different boolean representations."""
    # Test various true representations
    test_cases = [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("off", False),
    ]
    
    for value, expected in test_cases:
        os.environ["USE_REAL_LISTINGS"] = value
        try:
            settings = Settings()
            assert settings.USE_REAL_LISTINGS is expected, f"Failed for value: {value}"
        finally:
            os.environ.pop("USE_REAL_LISTINGS", None)


def test_settings_repr_hides_secrets():
    """Verify that repr() doesn't expose sensitive values."""
    os.environ["JWT_SECRET"] = "super-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://user:password@host:5432/db"
    
    try:
        settings = Settings()
        repr_str = repr(settings)
        
        # Secrets should be masked
        assert "super-secret-key" not in repr_str
        assert "password" not in repr_str
        assert "***" in repr_str
        
        # Non-sensitive values should be visible
        assert "USE_REAL_LISTINGS" in repr_str
    finally:
        os.environ.pop("JWT_SECRET", None)
        os.environ.pop("DATABASE_URL", None)


def test_settings_missing_jwt_secret_warns():
    """Verify that missing JWT_SECRET triggers a warning."""
    # Clear JWT_SECRET
    old_secret = os.environ.pop("JWT_SECRET", None)
    
    try:
        with pytest.warns(UserWarning, match="JWT_SECRET is not set"):
            settings = Settings()
            assert settings.JWT_SECRET == ""
    finally:
        if old_secret:
            os.environ["JWT_SECRET"] = old_secret
