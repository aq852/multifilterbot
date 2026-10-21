from datetime import datetime, timezone
from typing import Any

from app.database import get_database


async def save_file_for_user(user_id: int, chat_id: int, message_id: int) -> bool:
    result = await get_database().saved_files.update_one(
        {"user_id": user_id, "chat_id": chat_id, "message_id": message_id},
        {"$set": {"created_at": datetime.now(timezone.utc)}}, upsert=True
    )
    return result.upserted_id is not None or result.modified_count > 0


async def remove_saved_file(user_id: int, chat_id: int, message_id: int) -> bool:
    result = await get_database().saved_files.delete_one(
        {"user_id": user_id, "chat_id": chat_id, "message_id": message_id}
    )
    return result.deleted_count > 0


async def list_saved_files(user_id: int, limit: int = 10, skip: int = 0) -> list[dict[str, Any]]:
    cursor = get_database().saved_files.find(
        {"user_id": user_id}, {"chat_id": 1, "message_id": 1}
    ).sort("created_at", -1).skip(skip).limit(limit)
    saved = await cursor.to_list(length=limit)
    targets = [{"chat_id": item["chat_id"], "message_id": item["message_id"]} for item in saved]
    if not targets:
        return []
    files = await get_database().files.find({"$or": targets}).to_list(length=limit)
    by_target = {(item["chat_id"], item["message_id"]): item for item in files}
    return [by_target[target["chat_id"], target["message_id"]] for target in targets
            if (target["chat_id"], target["message_id"]) in by_target]


async def clear_saved_files(user_id: int) -> int:
    result = await get_database().saved_files.delete_many({"user_id": user_id})
    return result.deleted_count
