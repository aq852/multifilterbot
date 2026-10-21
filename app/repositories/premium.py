from datetime import datetime, timedelta, timezone
from typing import Any

from app.database import get_database


async def activate_premium(user_id: int, plan_id: str, days: int, charge_id: str) -> datetime | None:
    payment = await get_database().payments.update_one(
        {"charge_id": charge_id},
        {"$setOnInsert": {"user_id": user_id, "plan_id": plan_id, "charge_id": charge_id,
                           "created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    if payment.upserted_id is None:
        return None

    user: dict[str, Any] | None = await get_database().users.find_one({"_id": user_id})
    now = datetime.now(timezone.utc)
    current = user.get("premium_until") if user else None
    if current and current > now:
        expires_at = current + timedelta(days=days)
    else:
        expires_at = now + timedelta(days=days)
    await get_database().users.update_one(
        {"_id": user_id},
        {"$set": {"is_premium": True, "premium_until": expires_at}},
        upsert=True,
    )
    return expires_at


async def premium_status(user_id: int) -> datetime | None:
    user = await get_database().users.find_one({"_id": user_id}, {"premium_until": 1})
    expires_at = user.get("premium_until") if user else None
    if not expires_at or expires_at <= datetime.now(timezone.utc):
        return None
    return expires_at

