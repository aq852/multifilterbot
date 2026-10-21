from typing import Any

from app.database import get_database


async def set_auto_approve(enabled: bool) -> None:
    await get_database().bot_settings.update_one(
        {"_id": "auto_approve"}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def auto_approve_enabled() -> bool:
    setting = await get_database().bot_settings.find_one({"_id": "auto_approve"})
    return bool(setting and setting.get("enabled"))


async def set_reaction(chat_id: int, emoji: str) -> None:
    await get_database().reaction_rules.update_one(
        {"_id": chat_id}, {"$set": {"emoji": emoji}}, upsert=True
    )


async def remove_reaction(chat_id: int) -> bool:
    result = await get_database().reaction_rules.delete_one({"_id": chat_id})
    return result.deleted_count == 1


async def reaction_for_chat(chat_id: int) -> str | None:
    rule: dict[str, Any] | None = await get_database().reaction_rules.find_one({"_id": chat_id})
    return rule.get("emoji") if rule else None


async def list_reactions() -> list[dict[str, Any]]:
    return await get_database().reaction_rules.find().sort("_id", 1).to_list(length=100)

