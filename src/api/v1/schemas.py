"""
API Schemas Module

This module defines all Pydantic models used for request validation
and response serialization in the API layer.

Responsibilities:
    - Validate incoming request data
    - Serialize outgoing response data
    - Define API contracts
    - Provide type hints for IDE support

Note:
    These schemas are API-specific and may differ from domain models.
    They serve as a contract between the client and the API.

Example:
    >>> from pydantic import BaseModel
    >>>
    >>> class RegisterRequest(BaseModel):
    ...     email: str
    ...     password: str
    ...     full_name: str
    >>>
    >>> # Automatic validation
    >>> data = RegisterRequest(email="invalid", password="123", full_name="")
    >>> # Raises ValidationError
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from core.models.user import User


class RegisterRequest(BaseModel):
    """
    User registration request schema.

    Validates user input for registration endpoint.

    Attributes:
        email: Valid email address
        password: Password (min 8 chars, must contain uppercase, lowercase, digit)
        full_name: User's full name (min 2 chars)

    Example:
        >>> request = RegisterRequest(
        ...     email="john@example.com",
        ...     password="SecurePass123!",
        ...     full_name="John Doe"
        ... )
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    full_name: str = Field(
        ..., min_length=2, max_length=100, description="User's full name"
    )

    @validator("password")
    def validate_password(cls, v):
        """Ensure password meets security requirements"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """
    User login request schema.

    Attributes:
        email: User's email
        password: User's password
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    JWT token response schema.

    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")

    Example:
        >>> response = TokenResponse(
        ...     access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        ...     token_type="bearer"
        ... )
    """

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    User response schema.

    Serializes user data for API responses.
    Never includes sensitive information like passwords.

    Attributes:
        id: User's unique identifier
        email: User's email address
        full_name: User's full name
        is_active: Whether user account is active
        created_at: Account creation timestamp
    """

    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        """
        Convert domain User model to API response schema.

        Args:
            user: Domain User model

        Returns:
            UserResponse: API-serializable user data
        """
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )
