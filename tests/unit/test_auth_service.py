"""
Unit tests for AuthService.

Tests business logic in isolation using mocks.
No database, no HTTP, no external dependencies.
"""

import pytest
from unittest.mock import AsyncMock
from core.services.auth_service import AuthService
from core.models.user import User
from core.exceptions import DuplicateEmailError


@pytest.fixture
def mock_user_repo():
    """Create mock user repository"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repo):
    """Create auth service with mocked dependencies"""
    return AuthService(mock_user_repo)


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_user_repo):
    """Test successful user registration"""
    # Arrange
    mock_user_repo.get_by_email.return_value = None  # Email doesn't exist
    mock_user_repo.create.return_value = User(
        id="123",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
    )

    # Act
    user = await auth_service.register(
        email="test@example.com", password="password123", full_name="Test User"
    )

    # Assert
    assert user.id == "123"
    assert user.email == "test@example.com"
    mock_user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service, mock_user_repo):
    """Test registration with existing email"""
    # Arrange
    mock_user_repo.get_by_email.return_value = User(
        id="123",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Existing User",
    )

    # Act & Assert
    with pytest.raises(DuplicateEmailError):
        await auth_service.register(
            email="test@example.com", password="password123", full_name="New User"
        )
