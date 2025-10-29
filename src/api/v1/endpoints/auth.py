"""
Authentication Endpoints Module

This module handles all authentication-related HTTP endpoints including
user registration, login, token refresh, and password management.

Responsibilities:
    - Receive authentication requests
    - Validate input using Pydantic schemas
    - Delegate business logic to AuthService
    - Return appropriate HTTP responses
    - Handle authentication errors

Dependencies:
    - FastAPI router for endpoint definitions
    - Pydantic schemas for validation
    - AuthService for business logic

Example:
    >>> # Client makes request:
    >>> POST /api/v1/auth/register
    >>> {
    ...     "email": "user@example.com",
    ...     "password": "SecurePass123!",
    ...     "full_name": "John Doe"
    ... }
    >>>
    >>> # Endpoint validates input and calls AuthService
    >>> # Returns 201 Created with user data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from api.v1.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from core.services.auth_service import AuthService
from config.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.

    Args:
        data: User registration data (email, password, full_name)
        auth_service: Injected authentication service

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException 400: If email already exists or validation fails
        HTTPException 422: If input data is invalid

    Example:
        Request:
            POST /api/v1/auth/register
            {
                "email": "john@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }

        Response (201):
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z"
            }
    """
    try:
        user = await auth_service.register(
            email=data.email, password=data.password, full_name=data.full_name
        )
        return UserResponse.from_domain(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return access token.

    Args:
        data: Login credentials (email, password)
        auth_service: Injected authentication service

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException 401: If credentials are invalid

    Example:
        Request:
            POST /api/v1/auth/login
            {
                "email": "john@example.com",
                "password": "SecurePass123!"
            }

        Response (200):
            {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
    """
    user = await auth_service.authenticate(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(user.id)
    return TokenResponse(access_token=access_token, token_type="bearer")
