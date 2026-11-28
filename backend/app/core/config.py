"""Centralized application settings using pydantic-settings.

All configuration is loaded from environment variables.
Supports a local .env file without requiring it to be committed.
"""

import os
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/aqar",
        description="PostgreSQL connection string",
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string",
    )

    # Authentication
    JWT_SECRET: str = Field(
        default="",
        description="Secret key for JWT token signing (must be set in production)",
    )

    # CORS - stored as comma-separated string in env, converted to list
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Allowed CORS origins as comma-separated string",
    )

    # Feature flags for fake/real service switching
    USE_REAL_LISTINGS: bool = Field(
        default=False,
        description="Use real listings implementation",
    )
    USE_REAL_FINANCE: bool = Field(
        default=False,
        description="Use real finance service implementation",
    )
    USE_REAL_RAG: bool = Field(
        default=False,
        description="Use real RAG implementation",
    )
    USE_REAL_CONVERSATIONS: bool = Field(
        default=False,
        description="Use real conversation store implementation",
    )
    USE_REAL_LEADS: bool = Field(
        default=False,
        description="Use real leads service implementation",
    )
    USE_REAL_AGENT: bool = Field(
        default=False,
        description="Use real agent implementation",
    )

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list.
        
        Parses the comma-separated CORS_ORIGINS string into a list.
        """
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return [self.CORS_ORIGINS]

    def model_post_init(self, __context: Any) -> None:
        """Validate critical settings after initialization."""
        # Warn if JWT_SECRET is not set (but don't fail - allow development mode)
        if not self.JWT_SECRET:
            import warnings
            warnings.warn(
                "JWT_SECRET is not set. Using empty secret is insecure for production.",
                UserWarning,
                stacklevel=2,
            )

    def __repr__(self) -> str:
        """Safe representation that doesn't expose secrets."""
        return (
            f"Settings("
            f"DATABASE_URL={'***' if self.DATABASE_URL else 'not set'}, "
            f"REDIS_URL={'***' if self.REDIS_URL else 'not set'}, "
            f"JWT_SECRET={'***' if self.JWT_SECRET else 'not set'}, "
            f"CORS_ORIGINS={self.cors_origins_list}, "
            f"USE_REAL_LISTINGS={self.USE_REAL_LISTINGS}, "
            f"USE_REAL_FINANCE={self.USE_REAL_FINANCE}, "
            f"USE_REAL_RAG={self.USE_REAL_RAG}, "
            f"USE_REAL_CONVERSATIONS={self.USE_REAL_CONVERSATIONS}, "
            f"USE_REAL_LEADS={self.USE_REAL_LEADS}, "
            f"USE_REAL_AGENT={self.USE_REAL_AGENT}"
            ")"
        )


# Global settings instance - loaded once at module import
settings = Settings()


# Convenience function for accessing settings
def get_settings() -> Settings:
    """Return the global settings instance.
    
    This can be used as a dependency in FastAPI endpoints if needed.
    """
    return settings
