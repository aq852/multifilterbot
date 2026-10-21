from datetime import datetime, timezone
from typing import Any

from app.database import get_database


async def record_admin_action(
    user_id: int,
    chat_id: int | None,
    action: str,
    username: str | None = None,
) -> None:
    await get_database().audit_logs.insert_one(
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "action": action[:80],
            "created_at": datetime.now(timezone.utc),
        }
    )


async def list_admin_actions(limit: int = 20) -> list[dict[str, Any]]:
    return await get_database().audit_logs.find({}).sort("created_at", -1).limit(limit).to_list(length=limit)
