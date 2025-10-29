"""
Security Utilities Module

This module provides security-related helper functions for password hashing,
JWT token management, and other cryptographic operations.

Responsibilities:
    - Password hashing and verification
    - JWT token creation and validation
    - Secure random generation

Example:
    >>> from utils.security import get_password_hash, verify_password
    >>>
    >>> hashed = get_password_hash("my_password")
    >>> is_valid = verify_password("my_password", hashed)  # True
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Uses bcrypt for secure password comparison.

    Args:
        plain_password: Plain text password
        hashed_password: BCrypt hashed password

    Returns:
        bool: True if password matches

    Example:
        >>> hashed = "$2b$12$KIXl.LGfNf3Vw9Zd2kN3dO..."
        >>> is_valid = verify_password("MyPassword123!", hashed)
        >>> print(is_valid)  # True or False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: BCrypt hashed password

    Example:
        >>> hashed = get_password_hash("MySecurePassword123!")
        >>> print(hashed)  # "$2b$12$KIXl.LGfNf3Vw9Zd2kN3dO..."
        >>>
        >>> # Store this in database, never store plain password!
        >>> user.hashed_password = hashed
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload to encode in token (usually {"sub": user_id})
        expires_delta: Token expiration time (default from settings)

    Returns:
        str: JWT token

    Example:
        >>> token = create_access_token(
        ...     data={"sub": "user_123"},
        ...     expires_delta=timedelta(minutes=30)
        ... )
        >>> print(token)  # "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>>
        >>> # Send to client in response
        >>> return {"access_token": token, "token_type": "bearer"}
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload if valid, None if invalid/expired

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = decode_access_token(token)
        >>> if payload:
        ...     user_id = payload.get("sub")
        ...     print(f"User ID: {user_id}")
        ... else:
        ...     print("Invalid token")
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
