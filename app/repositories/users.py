from datetime import datetime, timezone
import re
from typing import Any

from pymongo import ReturnDocument

from app.database import get_database


async def upsert_user(
    user_id: int, username: str | None, first_name: str | None, referrer_id: int | None = None
) -> bool:
    now = datetime.now(timezone.utc)
    result = await get_database().users.update_one(
        {"_id": user_id},
        {"$set": {"username": username, "first_name": first_name, "last_seen": now},
         "$setOnInsert": {"is_banned": False, "is_premium": False, "created_at": now,
                           "referrer_id": referrer_id}},
        upsert=True,
    )
    return result.upserted_id is not None


async def get_user(user_id: int) -> dict[str, Any] | None:
    return await get_database().users.find_one({"_id": user_id})


async def get_user_by_username(username: str) -> dict[str, Any] | None:
    value = re.escape(username.lstrip("@"))
    return await get_database().users.find_one({"username": {"$regex": f"^{value}$", "$options": "i"}})


async def list_users(limit: int = 25, skip: int = 0) -> list[dict[str, Any]]:
    return await get_database().users.find(
        {}, {"username": 1, "first_name": 1, "is_banned": 1, "is_blocked": 1, "is_premium": 1, "warnings": 1}
    ).sort("last_seen", -1).skip(skip).limit(limit).to_list(length=limit)


async def list_user_ids() -> list[int]:
    users = await get_database().users.find(
        {"is_blocked": {"$ne": True}, "is_banned": {"$ne": True}}, {"_id": 1}
    ).to_list(length=None)
    return [user["_id"] for user in users]


async def mark_user_blocked(user_id: int) -> None:
    await get_database().users.update_one({"_id": user_id}, {"$set": {"is_blocked": True}})


async def set_user_blocked(user_id: int, blocked: bool) -> None:
    await get_database().users.update_one(
        {"_id": user_id}, {"$set": {"is_blocked": blocked}}, upsert=True
    )


async def set_banned(user_id: int, banned: bool) -> None:
    await get_database().users.update_one({"_id": user_id}, {"$set": {"is_banned": banned}}, upsert=True)


async def is_banned(user_id: int) -> bool:
    user = await get_database().users.find_one({"_id": user_id}, {"is_banned": 1})
    return bool(user and user.get("is_banned"))


async def add_warning(user_id: int) -> int:
    result = await get_database().users.find_one_and_update(
        {"_id": user_id}, {"$inc": {"warnings": 1}},
        upsert=True, return_document=ReturnDocument.AFTER,
    )
    return int(result.get("warnings", 1)) if result else 1


async def get_warnings(user_id: int) -> int:
    user = await get_database().users.find_one({"_id": user_id}, {"warnings": 1})
    return int(user.get("warnings", 0)) if user else 0


async def clear_warnings(user_id: int) -> None:
    await get_database().users.update_one({"_id": user_id}, {"$set": {"warnings": 0}}, upsert=True)
