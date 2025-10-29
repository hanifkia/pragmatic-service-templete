"""
End-to-end tests for user registration and login flow.

Tests the complete flow through API, service, and database.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    """Test complete user registration and login flow"""
    # Step 1: Register user
    register_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test@example.com"

    # Step 2: Login with credentials
    login_data = {"email": "test@example.com", "password": "SecurePass123!"}

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data

    # Step 3: Access protected endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == "test@example.com"
