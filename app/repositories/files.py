from typing import Any

from app.database import get_database
from app.services.search import parse_media_filter, search_pattern


async def save_file(document: dict[str, Any]) -> bool:
    result = await get_database().files.update_one(
        {"chat_id": document["chat_id"], "message_id": document["message_id"]},
        {"$set": document}, upsert=True
    )
    return result.upserted_id is not None or result.modified_count > 0


async def search_files(query: str, limit: int = 5, skip: int = 0, media_type: str | None = None) -> list[dict[str, Any]]:
    query, detected_type = parse_media_filter(query)
    media_type = media_type or detected_type
    pattern = search_pattern(query)
    filters: dict[str, Any] = {"$or": [{"normalized_title": {"$regex": pattern}},
                                        {"search_terms": {"$regex": pattern}}]}
    if media_type:
        filters["media_type"] = media_type
    cursor = get_database().files.find(
        filters,
        {"name": 1, "title": 1, "chat_id": 1, "message_id": 1, "media_type": 1, "size": 1},
    ).sort("title", 1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)


async def count_search_files(query: str) -> int:
    query, media_type = parse_media_filter(query)
    pattern = search_pattern(query)
    filters: dict[str, Any] = {"$or": [{"normalized_title": {"$regex": pattern}},
                                        {"search_terms": {"$regex": pattern}}]}
    if media_type:
        filters["media_type"] = media_type
    return await get_database().files.count_documents(filters)


async def get_file(chat_id: int, message_id: int) -> dict[str, Any] | None:
    return await get_database().files.find_one({"chat_id": chat_id, "message_id": message_id})
