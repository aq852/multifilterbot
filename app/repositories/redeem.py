from typing import Any

from pymongo import ReturnDocument

from app.database import get_database
from app.services.redeem import normalize_code


async def create_redeem_code(code: str, days: int, uses: int) -> bool:
    code = normalize_code(code)
    if not code or days < 1 or uses < 1:
        return False
    result = await get_database().redeem_codes.update_one(
        {"_id": code},
        {"$setOnInsert": {"days": days, "uses_remaining": uses, "uses_total": uses}},
        upsert=True,
    )
    return result.upserted_id is not None


async def claim_redeem_code(code: str, user_id: int) -> dict[str, Any] | None:
    code = normalize_code(code)
    return await get_database().redeem_codes.find_one_and_update(
        {"_id": code, "uses_remaining": {"$gt": 0}, "redeemed_by": {"$ne": user_id}},
        {"$inc": {"uses_remaining": -1}, "$addToSet": {"redeemed_by": user_id}},
        return_document=ReturnDocument.AFTER,
    )

