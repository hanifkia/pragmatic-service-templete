from motor.motor_asyncio import AsyncIOMotorDatabase
from core.interfaces.repositories import UserRepository
from core.models.user import User


class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        doc = await self.db.users.find_one({"_id": user_id})
        if not doc:
            return None
        return self._to_domain(doc)

    async def create(self, user: User) -> User:
        doc = self._to_document(user)
        result = await self.db.users.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    def _to_domain(self, doc: dict) -> User:
        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            hashed_password=doc["hashed_password"],
            full_name=doc["full_name"],
            is_active=doc["is_active"],
            created_at=doc["created_at"],
        )
