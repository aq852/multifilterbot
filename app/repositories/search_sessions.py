from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.database import get_database


async def create_search_session(user_id: int, query: str) -> str:
    token = uuid4().hex[:12]
    await get_database().search_sessions.insert_one({
        "_id": token,
        "user_id": user_id,
        "query": query,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15),
    })
    return token


async def get_search_session(token: str, user_id: int) -> dict | None:
    return await get_database().search_sessions.find_one({
        "_id": token,
        "user_id": user_id,
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })

