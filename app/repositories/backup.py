from typing import Any

from app.database import get_database


async def export_catalog() -> dict[str, Any]:
    db = get_database()
    files = await db.files.find({}, {"_id": 0}).to_list(length=None)
    channels = await db.channels.find({}, {"_id": 1, "title": 1, "added_by": 1}).to_list(length=None)
    return {
        "format": "multifilterbot-catalog-v1",
        "files": files,
        "channels": [{"chat_id": item["_id"], **{key: value for key, value in item.items() if key != "_id"}} for item in channels],
    }


async def import_catalog(payload: dict[str, Any]) -> tuple[int, int]:
    db = get_database()
    imported_files = 0
    imported_channels = 0
    for item in payload.get("files", []):
        if not isinstance(item, dict) or "chat_id" not in item or "message_id" not in item:
            continue
        document = {key: value for key, value in item.items() if key != "_id"}
        await db.files.update_one(
            {"chat_id": document["chat_id"], "message_id": document["message_id"]},
            {"$set": document},
            upsert=True,
        )
        imported_files += 1
    for item in payload.get("channels", []):
        if not isinstance(item, dict) or "chat_id" not in item:
            continue
        chat_id = item["chat_id"]
        document = {key: value for key, value in item.items() if key != "chat_id"}
        await db.channels.update_one({"_id": chat_id}, {"$set": document}, upsert=True)
        imported_channels += 1
    return imported_files, imported_channels
