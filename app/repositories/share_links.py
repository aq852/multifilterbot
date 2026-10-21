from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Any

from app.database import get_database


async def create_expiring_link(
    chat_id: int, message_id: int, created_by: int, hours: int = 24
) -> str:
    token = uuid4().hex[:16]
    await get_database().share_links.insert_one(
        {
            "_id": token,
            "chat_id": chat_id,
            "message_id": message_id,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=hours),
        }
    )
    return token


async def get_active_link(token: str) -> dict[str, Any] | None:
    return await get_database().share_links.find_one(
        {"_id": token, "expires_at": {"$gt": datetime.now(timezone.utc)}}
    )
