"""
Application Settings Module

This module defines all configuration settings for the application
using Pydantic for validation and environment variable loading.

Responsibilities:
    - Load configuration from environment variables
    - Validate configuration values
    - Provide type-safe settings access
    - Handle different environments (dev, staging, prod)

Example:
    >>> from config.settings import settings
    >>>
    >>> print(settings.DATABASE_URL)
    >>> print(settings.DEBUG)
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment Variables:
        - DATABASE_URL: PostgreSQL connection string
        - REDIS_URL: Redis connection string
        - SECRET_KEY: JWT signing key
        - DEBUG: Enable debug mode
        - LOG_LEVEL: Logging level
        - ACCESS_TOKEN_EXPIRE_MINUTES: JWT expiration

    Example .env file:
        DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
        REDIS_URL=redis://localhost:6379
        SECRET_KEY=your-secret-key-here
        DEBUG=true
        LOG_LEVEL=INFO
        ACCESS_TOKEN_EXPIRE_MINUTES=30

    Usage:
        >>> from config.settings import settings
        >>>
        >>> if settings.DEBUG:
        ...     print("Running in debug mode")
        >>>
        >>> engine = create_engine(settings.DATABASE_URL)
    """

    # Application
    APP_NAME: str = "FastAPI Service"
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    # Redis
    REDIS_URL: str = Field(..., description="Redis connection URL")

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure DATABASE_URL is properly formatted"""
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must start with 'postgresql'")
        return v

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Ensure SECRET_KEY is strong enough"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
