"""
Integration tests for PostgresUserRepository.

Tests actual database operations using test database.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.user import User
from adapters.database.postgres.repositories import PostgresUserRepository


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating user in database"""
    # Arrange
    repo = PostgresUserRepository(db_session)
    user = User(
        id=None,
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
    )

    # Act
    created_user = await repo.create(user)

    # Assert
    assert created_user.id is not None
    assert created_user.email == "test@example.com"
    assert created_user.created_at is not None


@pytest.mark.asyncio
async def test_get_by_email(db_session: AsyncSession):
    """Test retrieving user by email"""
    # Arrange
    repo = PostgresUserRepository(db_session)
    user = User(
        id=None,
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
    )
    await repo.create(user)

    # Act
    found_user = await repo.get_by_email("test@example.com")

    # Assert
    assert found_user is not None
    assert found_user.email == "test@example.com"
