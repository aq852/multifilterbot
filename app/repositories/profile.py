import asyncio
from typing import Any

from app.database import get_database
from app.repositories.premium import premium_status
from app.repositories.requests import user_open_requests
from app.repositories.users import get_user


async def get_profile(user_id: int) -> dict[str, Any]:
    db = get_database()
    user, premium_until, saved_count, request_items, history_count = await asyncio.gather(
        get_user(user_id),
        premium_status(user_id),
        db.saved_files.count_documents({"user_id": user_id}),
        user_open_requests(user_id),
        db.user_searches.count_documents({"user_id": user_id}),
    )
    return {
        "user": user or {},
        "premium_until": premium_until,
        "saved_count": saved_count,
        "open_requests": len(request_items),
        "history_count": history_count,
    }
