"""
Dependency Injection Configuration Module

This module configures dependency injection for the entire application.
This is where you wire up interfaces to implementations.

Responsibilities:
    - Wire interfaces to concrete implementations
    - Manage dependency lifecycles
    - Provide factory functions for FastAPI dependencies

Key Concept:
    This is the ONLY place where you choose which implementation to use.
    Want to switch from Postgres to MongoDB? Change ONE line here.

Example:
    >>> # In this file
    >>> def get_user_repository() -> UserRepository:
    ...     return PostgresUserRepository(session)  # ← Change this line
    ...     # return MongoUserRepository(client)    # ← To this
    >>>
    >>> # Everywhere else uses the interface
    >>> async def endpoint(repo: UserRepository = Depends(get_user_repository)):
    ...     # Works with ANY implementation!
    ...     pass
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import redis.asyncio as redis
from config.settings import settings
from core.interfaces.repositories import UserRepository, CacheRepository
from core.services.auth_service import AuthService
from adapters.database.postgres.repositories import PostgresUserRepository
from adapters.database.postgres.models import Base
from adapters.cache.redis import RedisCache

# Database Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Redis Client
redis_client = redis.from_url(
    settings.REDIS_URL, encoding="utf-8", decode_responses=True
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide database session for dependency injection.

    This is a FastAPI dependency that provides a database session
    for each request and ensures proper cleanup.

    Yields:
        AsyncSession: SQLAlchemy async session

    Example:
        >>> @router.get("/users")
        >>> async def get_users(db: AsyncSession = Depends(get_db)):
        ...     # Use db session
        ...     result = await db.execute(select(UserModel))
        ...     return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """
    Provide UserRepository implementation.

    🔥 KEY POINT: This is where you choose the implementation!
    Want to switch databases? Change this function.

    Returns:
        UserRepository: Repository implementation (currently Postgres)

    Example - Switching implementations:
        >>> # Current (Postgres)
        >>> return PostgresUserRepository(db)
        >>>
        >>> # Switch to MongoDB (just change this line!)
        >>> return MongoUserRepository(mongo_client)
        >>>
        >>> # Use mock for testing
        >>> return MockUserRepository()
    """
    return PostgresUserRepository(db)


async def get_cache_repository() -> CacheRepository:
    """
    Provide CacheRepository implementation.

    Returns:
        CacheRepository: Cache implementation (currently Redis)

    Example - Switching cache:
        >>> # Current (Redis)
        >>> return RedisCache(redis_client)
        >>>
        >>> # Switch to Memcached
        >>> return MemcachedCache(memcached_client)
    """
    return RedisCache(redis_client)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """
    Provide AuthService with injected dependencies.

    Args:
        user_repo: Injected user repository

    Returns:
        AuthService: Configured authentication service

    Example:
        >>> @router.post("/register")
        >>> async def register(
        ...     data: RegisterRequest,
        ...     auth_service: AuthService = Depends(get_auth_service)
        ... ):
        ...     user = await auth_service.register(...)
        ...     return user
    """
    return AuthService(user_repo)


async def init_db():
    """
    Initialize database (create tables).

    Call this on application startup to ensure tables exist.

    Example:
        >>> @app.on_event("startup")
        >>> async def startup():
        ...     await init_db()
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections.

    Call this on application shutdown for cleanup.

    Example:
        >>> @app.on_event("shutdown")
        >>> async def shutdown():
        ...     await close_db()
    """
    await engine.dispose()
