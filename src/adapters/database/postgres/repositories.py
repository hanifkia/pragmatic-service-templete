"""
PostgreSQL Repository Implementation Module

This module implements the repository interfaces using PostgreSQL and SQLAlchemy.
This is ONE possible implementation - you could have MongoDB, DynamoDB, etc.

Responsibilities:
    - Implement repository interfaces for PostgreSQL
    - Handle database-specific operations
    - Convert between database models and domain models
    - Manage transactions

Key Concept:
    This is in the adapters layer, so it depends on core interfaces
    but core NEVER depends on this. This enables easy database swapping.

Example:
    >>> # Can swap this implementation without changing business logic
    >>> postgres_repo = PostgresUserRepository(db_session)
    >>> mongo_repo = MongoUserRepository(mongo_client)
    >>>
    >>> # Service works with either
    >>> service = AuthService(postgres_repo)  # or
    >>> service = AuthService(mongo_repo)
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.interfaces.repositories import UserRepository
from core.models.user import User
from .models import UserModel


class PostgresUserRepository(UserRepository):
    """
    PostgreSQL implementation of UserRepository interface.

    This class translates between domain models (User) and
    database models (UserModel from SQLAlchemy).

    Attributes:
        session: SQLAlchemy async session for database operations

    Example:
        >>> from sqlalchemy.ext.asyncio import AsyncSession
        >>>
        >>> async def get_user(session: AsyncSession):
        ...     repo = PostgresUserRepository(session)
        ...     user = await repo.get_by_email("john@example.com")
        ...     return user
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session (injected by DI)
        """
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID from PostgreSQL.

        Implementation Details:
            1. Query database using SQLAlchemy
            2. Convert UserModel to domain User
            3. Return None if not found

        Args:
            user_id: User's unique identifier

        Returns:
            User: Domain user model or None
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        # Convert database model to domain model
        return self._to_domain(db_user)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email from PostgreSQL"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        return self._to_domain(db_user)

    async def create(self, user: User) -> User:
        """
        Create user in PostgreSQL.

        Implementation Details:
            1. Convert domain User to UserModel (SQLAlchemy)
            2. Add to session and commit
            3. Refresh to get generated values (id, timestamps)
            4. Convert back to domain model

        Args:
            user: Domain user model (id may be None)

        Returns:
            User: Created user with generated id and timestamps
        """
        db_user = UserModel(
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )

        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)

        return self._to_domain(db_user)

    async def update(self, user: User) -> User:
        """Update user in PostgreSQL"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise ValueError(f"User {user.id} not found")

        # Update fields
        db_user.email = user.email
        db_user.full_name = user.full_name
        db_user.is_active = user.is_active
        db_user.is_superuser = user.is_superuser

        await self.session.commit()
        await self.session.refresh(db_user)

        return self._to_domain(db_user)

    async def delete(self, user_id: str) -> bool:
        """Delete user from PostgreSQL"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return False

        await self.session.delete(db_user)
        await self.session.commit()
        return True

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users from PostgreSQL with pagination"""
        result = await self.session.execute(select(UserModel).offset(skip).limit(limit))
        db_users = result.scalars().all()

        return [self._to_domain(db_user) for db_user in db_users]

    def _to_domain(self, db_user: UserModel) -> User:
        """
        Convert SQLAlchemy model to domain model.

        This is a crucial translation layer that keeps domain models
        independent of database implementation.

        Args:
            db_user: SQLAlchemy UserModel

        Returns:
            User: Domain User model
        """
        return User(
            id=str(db_user.id),
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
