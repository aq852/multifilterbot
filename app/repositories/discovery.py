from typing import Any

from app.database import get_database
from app.services.search import normalize_title
from datetime import datetime, timezone


async def record_search(query: str) -> None:
    normalized = normalize_title(query)
    if not normalized:
        return
    await get_database().search_stats.update_one(
        {"_id": normalized},
        {"$inc": {"count": 1}, "$set": {"query": query.strip()}},
        upsert=True,
    )


async def record_user_search(user_id: int, query: str) -> None:
    normalized = normalize_title(query)
    if not normalized:
        return
    await get_database().user_searches.update_one(
        {"user_id": user_id, "normalized": normalized},
        {"$set": {"query": query.strip(), "last_used_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


async def user_search_history(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    return await get_database().user_searches.find(
        {"user_id": user_id}, {"query": 1, "last_used_at": 1}
    ).sort("last_used_at", -1).limit(limit).to_list(length=limit)


async def top_searches(limit: int = 10) -> list[dict[str, Any]]:
    return await get_database().search_stats.find().sort("count", -1).limit(limit).to_list(length=limit)


async def latest_files(limit: int = 10) -> list[dict[str, Any]]:
    cursor = get_database().files.find(
        {}, {"name": 1, "title": 1, "chat_id": 1, "message_id": 1, "media_type": 1}
    ).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
