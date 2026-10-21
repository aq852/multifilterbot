from typing import Any

from app.database import get_database
from app.repositories.channels import list_channels


async def channel_index_stats() -> list[dict[str, Any]]:
    channels = await list_channels()
    if not channels:
        return []
    ids = [channel["_id"] for channel in channels]
    rows = await get_database().files.aggregate([
        {"$match": {"chat_id": {"$in": ids}}},
        {"$group": {
            "_id": "$chat_id",
            "indexed_files": {"$sum": 1},
            "downloads": {"$sum": {"$ifNull": ["$downloads", 0]}},
            "last_indexed": {"$max": "$created_at"},
        }},
    ]).to_list(length=len(ids))
    by_id = {row["_id"]: row for row in rows}
    return [
        {
            "chat_id": channel["_id"],
            "title": channel.get("title") or str(channel["_id"]),
            "indexed_files": by_id.get(channel["_id"], {}).get("indexed_files", 0),
            "downloads": by_id.get(channel["_id"], {}).get("downloads", 0),
            "last_indexed": by_id.get(channel["_id"], {}).get("last_indexed"),
        }
        for channel in channels
    ]
