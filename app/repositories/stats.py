import asyncio
from datetime import datetime, timezone

from app.database import get_database


async def get_stats() -> dict[str, int]:
    db = get_database()
    users, channels, files, premium = await asyncio.gather(
        db.users.count_documents({}),
        db.channels.count_documents({}),
        db.files.count_documents({}),
        db.users.count_documents({"premium_until": {"$gt": datetime.now(timezone.utc)}}),
    )
    return {"users": users, "channels": channels, "files": files, "premium": premium}
