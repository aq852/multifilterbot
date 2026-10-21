from typing import Any

from app.database import get_database


async def add_channel(chat_id: int, title: str, added_by: int) -> None:
    await get_database().channels.update_one(
        {"_id": chat_id}, {"$set": {"title": title, "added_by": added_by}}, upsert=True
    )


async def remove_channel(chat_id: int) -> bool:
    result = await get_database().channels.delete_one({"_id": chat_id})
    return result.deleted_count == 1


async def list_channels() -> list[dict[str, Any]]:
    return await get_database().channels.find().sort("title", 1).to_list(length=100)


async def is_indexed_channel(chat_id: int) -> bool:
    return await get_database().channels.find_one({"_id": chat_id}) is not None

