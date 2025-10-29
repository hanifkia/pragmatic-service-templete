"""
Repository Interfaces Module

This module defines abstract interfaces (contracts) for data access.
These interfaces define WHAT operations are needed without specifying HOW they're implemented.

Responsibilities:
    - Define data access contracts
    - Enable dependency inversion
    - Allow multiple implementations (Postgres, MongoDB, etc.)
    - Facilitate testing with mocks

Key Principle:
    Core layer defines interfaces, adapters layer implements them.
    This is the dependency inversion principle in action.

Example:
    >>> # In core layer - define interface
    >>> class UserRepository(ABC):
    ...     @abstractmethod
    ...     async def get_by_id(self, user_id: str) -> Optional[User]:
    ...         pass
    >>>
    >>> # In adapters layer - implement for Postgres
    >>> class PostgresUserRepository(UserRepository):
    ...     async def get_by_id(self, user_id: str) -> Optional[User]:
    ...         # Postgres-specific implementation
    ...         pass
    >>>
    >>> # In adapters layer - implement for MongoDB
    >>> class MongoUserRepository(UserRepository):
    ...     async def get_by_id(self, user_id: str) -> Optional[User]:
    ...         # MongoDB-specific implementation
    ...         pass
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from core.models.user import User


class UserRepository(ABC):
    """
    Abstract interface for user data access.

    This interface defines all user-related data operations without
    specifying the implementation details (database, ORM, etc.).

    Benefits:
        - Business logic doesn't depend on specific database
        - Easy to swap databases (Postgres → MongoDB)
        - Easy to test with mock implementations
        - Enables multiple implementations simultaneously

    Example:
        >>> # Usage in service (depends on interface, not implementation)
        >>> class AuthService:
        ...     def __init__(self, user_repo: UserRepository):
        ...         self.user_repo = user_repo
        ...
        ...     async def get_user(self, user_id: str):
        ...         return await self.user_repo.get_by_id(user_id)
        >>>
        >>> # Can inject ANY implementation
        >>> service = AuthService(PostgresUserRepository())  # or
        >>> service = AuthService(MongoUserRepository())     # or
        >>> service = AuthService(MockUserRepository())      # for testing
    """

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User: User if found, None otherwise

        Example:
            >>> user = await user_repo.get_by_id("123e4567-e89b-12d3-a456-426614174000")
            >>> if user:
            ...     print(user.email)
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve user by email address.

        Args:
            email: User's email address

        Returns:
            User: User if found, None otherwise

        Example:
            >>> user = await user_repo.get_by_email("john@example.com")
        """
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user.

        Args:
            user: User entity to create (id may be None)

        Returns:
            User: Created user with generated ID and timestamps

        Example:
            >>> new_user = User(
            ...     id=None,
            ...     email="john@example.com",
            ...     hashed_password="...",
            ...     full_name="John Doe"
            ... )
            >>> created = await user_repo.create(new_user)
            >>> print(created.id)  # "123e4567-e89b-12d3-a456-426614174000"
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update existing user.

        Args:
            user: User entity with updated data

        Returns:
            User: Updated user

        Example:
            >>> user.full_name = "John Smith"
            >>> updated = await user_repo.update(user)
        """
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            bool: True if deleted, False if not found

        Example:
            >>> deleted = await user_repo.delete("123e4567-e89b-12d3-a456-426614174000")
            >>> if deleted:
            ...     print("User deleted successfully")
        """
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        List users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[User]: List of users

        Example:
            >>> users = await user_repo.list(skip=0, limit=10)
            >>> for user in users:
            ...     print(user.email)
        """
        pass


class CacheRepository(ABC):
    """
    Abstract interface for caching operations.

    Enables swapping cache implementations (Redis, Memcached, etc.)
    without changing business logic.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
