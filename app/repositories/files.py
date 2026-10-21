from typing import Any

from app.database import get_database
from app.services.search import search_pattern


async def save_file(document: dict[str, Any]) -> bool:
    result = await get_database().files.update_one(
        {"chat_id": document["chat_id"], "message_id": document["message_id"]},
        {"$set": document}, upsert=True
    )
    return result.upserted_id is not None or result.modified_count > 0


async def search_files(query: str, limit: int = 10) -> list[dict[str, Any]]:
    pattern = search_pattern(query)
    cursor = get_database().files.find(
        {"$or": [{"normalized_title": {"$regex": pattern}},
                  {"search_terms": {"$regex": pattern}}]},
        {"name": 1, "title": 1, "chat_id": 1, "message_id": 1, "media_type": 1, "size": 1},
    ).sort("title", 1).limit(limit)
    return await cursor.to_list(length=limit)

