"""
Authentication Service Module

This module contains the core business logic for authentication operations.
It orchestrates user registration, authentication, and token management.

Responsibilities:
    - Implement authentication business rules
    - Coordinate between repositories
    - Validate business constraints
    - Generate access tokens

Dependencies:
    - UserRepository (interface only)
    - Password hashing utilities
    - JWT token utilities

Does NOT:
    - Know about HTTP requests/responses
    - Access database directly (uses repository interface)
    - Handle API-specific concerns

Example:
    >>> auth_service = AuthService(user_repository)
    >>> user = await auth_service.register("john@example.com", "password", "John Doe")
    >>> token = auth_service.create_access_token(user.id)
"""

from typing import Optional
from datetime import timedelta
from core.interfaces.repositories import UserRepository
from core.models.user import User
from core.exceptions import DuplicateEmailError, InvalidCredentialsError
from utils.security import verify_password, get_password_hash, create_access_token
from config.settings import settings


class AuthService:
    """
    Authentication service for user registration and login.

    This service implements all authentication-related business logic
    without knowing about HTTP, databases, or other infrastructure concerns.

    Attributes:
        user_repo: Repository for user data access (abstraction)
    """

    def __init__(self, user_repo: UserRepository):
        """
        Initialize authentication service.

        Args:
            user_repo: User repository implementation (injected)
        """
        self.user_repo = user_repo

    async def register(self, email: str, password: str, full_name: str) -> User:
        """
        Register a new user.

        Business Rules:
            1. Email must be unique
            2. Password must be hashed before storage
            3. User account is active by default
            4. Created timestamp is set automatically

        Args:
            email: User's email address (must be unique)
            password: Plain text password (will be hashed)
            full_name: User's full name

        Returns:
            User: Newly created user

        Raises:
            DuplicateEmailError: If email already exists

        Example:
            >>> service = AuthService(user_repo)
            >>> user = await service.register(
            ...     email="john@example.com",
            ...     password="SecurePass123!",
            ...     full_name="John Doe"
            ... )
            >>> print(user.id)  # "123e4567-e89b-12d3-a456-426614174000"
        """
        # Check if email already exists (business rule)
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise DuplicateEmailError(f"Email {email} is already registered")

        # Create user with hashed password (business rule)
        user = User(
            id=None,  # Will be set by repository
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            created_at=None,  # Will be set by repository
        )

        # Persist user
        created_user = await self.user_repo.create(user)
        return created_user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.

        Business Rules:
            1. User must exist
            2. Password must match stored hash
            3. User account must be active

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            User: Authenticated user if credentials are valid
            None: If authentication fails

        Example:
            >>> service = AuthService(user_repo)
            >>> user = await service.authenticate("john@example.com", "SecurePass123!")
            >>> if user:
            ...     print(f"Welcome, {user.full_name}!")
            ... else:
            ...     print("Invalid credentials")
        """
        # Get user by email
        user = await self.user_repo.get_by_email(email)

        # Validate credentials
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    def create_access_token(self, user_id: str) -> str:
        """
        Create JWT access token for user.

        Args:
            user_id: User's unique identifier

        Returns:
            str: JWT access token

        Example:
            >>> token = service.create_access_token("123e4567-e89b-12d3-a456-426614174000")
            >>> print(token)  # "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )
