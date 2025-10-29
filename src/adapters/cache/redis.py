"""
Redis Cache Implementation Module

This module implements the CacheRepository interface using Redis.
This is ONE possible implementation - you could use Memcached, etc.

Responsibilities:
    - Implement cache interface for Redis
    - Handle Redis-specific operations
    - Manage connection pooling
    - Handle serialization/deserialization

Example:
    >>> redis_cache = RedisCache(redis_client)
    >>> await redis_cache.set("user:123", json.dumps(user_data), expire=3600)
    >>> data = await redis_cache.get("user:123")
"""

from typing import Optional
import redis.asyncio as redis
from core.interfaces.repositories import CacheRepository


class RedisCache(CacheRepository):
    """
    Redis implementation of CacheRepository interface.

    Provides caching functionality using Redis as the backend.
    Useful for:
        - Session storage
        - API response caching
        - Rate limiting
        - Temporary data storage

    Attributes:
        client: Redis async client

    Example:
        >>> from redis.asyncio import Redis
        >>>
        >>> redis_client = Redis(host="localhost", port=6379)
        >>> cache = RedisCache(redis_client)
        >>>
        >>> # Store user session
        >>> await cache.set("session:abc123", user_data, expire=3600)
        >>>
        >>> # Retrieve session
        >>> data = await cache.get("session:abc123")
    """

    def __init__(self, client: redis.Redis):
        """
        Initialize Redis cache.

        Args:
            client: Redis async client (injected by DI)
        """
        self.client = client

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis cache.

        Args:
            key: Cache key

        Returns:
            str: Cached value or None if not found/expired

        Example:
            >>> value = await cache.get("user:123:profile")
            >>> if value:
            ...     user_data = json.loads(value)
        """
        value = await self.client.get(key)
        return value.decode("utf-8") if value else None

    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """
        Set value in Redis cache with expiration.

        Args:
            key: Cache key
            value: Value to cache (should be string/JSON)
            expire: Expiration time in seconds (default 1 hour)

        Returns:
            bool: True if successful

        Example:
            >>> import json
            >>> user_data = json.dumps({"id": "123", "name": "John"})
            >>> await cache.set("user:123", user_data, expire=1800)
        """
        return await self.client.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        """
        Delete value from Redis cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key was deleted

        Example:
            >>> await cache.delete("user:123:profile")
        """
        result = await self.client.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists

        Example:
            >>> if await cache.exists("user:123:profile"):
            ...     print("Cache hit!")
            ... else:
            ...     print("Cache miss - fetch from database")
        """
        return await self.client.exists(key) > 0
