from datetime import datetime, timezone
from typing import Any

from app.database import get_database


async def upsert_user(user_id: int, username: str | None, first_name: str | None) -> None:
    now = datetime.now(timezone.utc)
    await get_database().users.update_one(
        {"_id": user_id},
        {"$set": {"username": username, "first_name": first_name, "last_seen": now},
         "$setOnInsert": {"is_banned": False, "is_premium": False, "created_at": now}},
        upsert=True,
    )


async def get_user(user_id: int) -> dict[str, Any] | None:
    return await get_database().users.find_one({"_id": user_id})


async def list_user_ids() -> list[int]:
    users = await get_database().users.find({"is_blocked": {"$ne": True}}, {"_id": 1}).to_list(length=None)
    return [user["_id"] for user in users]


async def mark_user_blocked(user_id: int) -> None:
    await get_database().users.update_one({"_id": user_id}, {"$set": {"is_blocked": True}})
