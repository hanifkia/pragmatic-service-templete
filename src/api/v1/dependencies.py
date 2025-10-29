"""
API Dependencies Module

This module defines FastAPI dependencies for the API layer,
including authentication, rate limiting, and pagination.

Responsibilities:
    - Provide reusable dependencies for endpoints
    - Handle authentication and authorization
    - Manage rate limiting
    - Provide pagination helpers

Example:
    >>> from fastapi import Depends
    >>> from api.v1.dependencies import get_current_user
    >>>
    >>> @router.get("/me")
    >>> async def get_me(user: User = Depends(get_current_user)):
    ...     return user
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.models.user import User
from core.interfaces.repositories import UserRepository
from config.dependencies import get_user_repository
from utils.security import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Get currently authenticated user from JWT token.

    This dependency extracts the JWT token from the Authorization header,
    validates it, and returns the corresponding user from the database.

    Args:
        credentials: JWT token from Authorization header
        user_repo: User repository for database access

    Returns:
        User: Authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If user account is inactive

    Example:
        >>> @router.get("/profile")
        >>> async def get_profile(user: User = Depends(get_current_user)):
        ...     return {"email": user.email, "name": user.full_name}
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure current user is a superuser.

    Args:
        current_user: Currently authenticated user

    Returns:
        User: Authenticated superuser

    Raises:
        HTTPException 403: If user is not a superuser

    Example:
        >>> @router.delete("/users/{user_id}")
        >>> async def delete_user(
        ...     user_id: str,
        ...     admin: User = Depends(get_current_active_superuser)
        ... ):
        ...     # Only superusers can access this endpoint
        ...     pass
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
