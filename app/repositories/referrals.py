from app.database import get_database


async def referral_count(user_id: int) -> int:
    return await get_database().users.count_documents({"referrer_id": user_id})

