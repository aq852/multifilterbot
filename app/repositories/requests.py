from datetime import datetime, timezone
from uuid import uuid4

from app.database import get_database


async def create_request(user_id: int, query: str) -> str:
    request_id = uuid4().hex[:8]
    await get_database().file_requests.insert_one({
        "_id": request_id,
        "user_id": user_id,
        "query": query.strip(),
        "status": "open",
        "created_at": datetime.now(timezone.utc),
    })
    return request_id


async def open_requests(limit: int = 50) -> list[dict]:
    return await get_database().file_requests.find({"status": "open"}).sort("created_at", 1).limit(limit).to_list(length=limit)


async def close_request(request_id: str, closed_by: int) -> bool:
    result = await get_database().file_requests.update_one(
        {"_id": request_id, "status": "open"},
        {"$set": {"status": "closed", "closed_by": closed_by, "closed_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count == 1

