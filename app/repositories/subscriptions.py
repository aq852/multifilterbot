from typing import Any

from app.database import get_database


async def add_required_channel(chat_id: int, title: str, invite_url: str, added_by: int) -> None:
    await get_database().force_sub.update_one(
        {"_id": chat_id},
        {"$set": {"title": title, "invite_url": invite_url, "added_by": added_by}},
        upsert=True,
    )


async def remove_required_channel(chat_id: int) -> bool:
    result = await get_database().force_sub.delete_one({"_id": chat_id})
    return result.deleted_count == 1


async def list_required_channels() -> list[dict[str, Any]]:
    return await get_database().force_sub.find().sort("title", 1).to_list(length=20)

