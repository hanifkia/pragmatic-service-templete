"""
User Domain Model Module

This module defines the User entity, which represents a user in the business domain.
This is a pure domain model with no infrastructure dependencies.

Responsibilities:
    - Represent user entity in the business domain
    - Encapsulate user-related data
    - Provide domain-specific methods (if needed)

Does NOT:
    - Know about database tables or ORM
    - Know about HTTP requests/responses
    - Contain infrastructure code

Example:
    >>> user = User(
    ...     id="123",
    ...     email="john@example.com",
    ...     hashed_password="$2b$12$...",
    ...     full_name="John Doe",
    ...     is_active=True
    ... )
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    User domain entity.

    Represents a user in the business domain. This is a pure data class
    with no methods or business logic (following DDD principles).

    Attributes:
        id: Unique identifier (UUID as string)
        email: User's email address (unique)
        hashed_password: BCrypt hashed password
        full_name: User's full name
        is_active: Whether the account is active
        is_superuser: Whether user has admin privileges
        created_at: Account creation timestamp
        updated_at: Last update timestamp

    Example:
        >>> user = User(
        ...     id="123e4567-e89b-12d3-a456-426614174000",
        ...     email="john@example.com",
        ...     hashed_password="$2b$12$KIXl.LGfNf3Vw9Zd2kN3dO...",
        ...     full_name="John Doe",
        ...     is_active=True,
        ...     is_superuser=False,
        ...     created_at=datetime.utcnow()
        ... )
        >>> print(user.email)  # "john@example.com"
    """

    id: Optional[str]
    email: str
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_authenticated(self) -> bool:
        """
        Check if user has valid authentication.

        Returns:
            bool: True if user is active and authenticated

        Example:
            >>> if user.is_authenticated():
            ...     print("User can access protected resources")
        """
        return self.is_active and self.id is not None
