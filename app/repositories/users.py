from typing import Any

from app.database import get_database


async def upsert_user(user_id: int, username: str | None, first_name: str | None) -> None:
    await get_database().users.update_one(
        {"_id": user_id},
        {"$set": {"username": username, "first_name": first_name},
         "$setOnInsert": {"is_banned": False, "is_premium": False}},
        upsert=True,
    )


async def get_user(user_id: int) -> dict[str, Any] | None:
    return await get_database().users.find_one({"_id": user_id})

