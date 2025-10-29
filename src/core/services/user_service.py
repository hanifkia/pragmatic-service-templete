"""
Service with caching to reduce database load.
"""

import json
from typing import Optional


class UserService:
    def __init__(self, user_repo: UserRepository, cache: CacheRepository):
        self.user_repo = user_repo
        self.cache = cache

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user with cache layer.

        Flow:
            1. Check cache first
            2. If cache miss, query database
            3. Store in cache for next time
        """
        # Try cache first
        cache_key = f"user:{user_id}"
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            # Cache hit - deserialize and return
            user_dict = json.loads(cached_data)
            return User(**user_dict)

        # Cache miss - query database
        user = await self.user_repo.get_by_id(user_id)

        if user:
            # Store in cache for 1 hour
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
            }
            await self.cache.set(cache_key, json.dumps(user_dict), expire=3600)

        return user

    async def update_user(self, user: User) -> User:
        """
        Update user and invalidate cache.
        """
        updated_user = await self.user_repo.update(user)

        # Invalidate cache
        cache_key = f"user:{user.id}"
        await self.cache.delete(cache_key)

        return updated_user
