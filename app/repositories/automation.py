import random
from typing import Any

from app.database import get_database


async def set_auto_approve(enabled: bool) -> None:
    await get_database().bot_settings.update_one(
        {"_id": "auto_approve"}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def set_welcome(chat_id: int, enabled: bool) -> None:
    await get_database().bot_settings.update_one(
        {"_id": f"welcome:{chat_id}"}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def welcome_enabled(chat_id: int) -> bool:
    setting = await get_database().bot_settings.find_one({"_id": f"welcome:{chat_id}"})
    return bool(setting and setting.get("enabled"))


async def set_goodbye(chat_id: int, enabled: bool) -> None:
    await get_database().bot_settings.update_one(
        {"_id": f"goodbye:{chat_id}"}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def goodbye_enabled(chat_id: int) -> bool:
    setting = await get_database().bot_settings.find_one({"_id": f"goodbye:{chat_id}"})
    return bool(setting and setting.get("enabled"))


async def set_member_message(chat_id: int, kind: str, template: str | None) -> None:
    key = f"{kind}_template:{chat_id}"
    if template:
        await get_database().bot_settings.update_one(
            {"_id": key}, {"$set": {"template": template}}, upsert=True
        )
    else:
        await get_database().bot_settings.delete_one({"_id": key})


async def member_message_template(chat_id: int, kind: str) -> str | None:
    setting = await get_database().bot_settings.find_one({"_id": f"{kind}_template:{chat_id}"})
    return setting.get("template") if setting else None


async def auto_approve_enabled() -> bool:
    setting = await get_database().bot_settings.find_one({"_id": "auto_approve"})
    return bool(setting and setting.get("enabled"))


async def set_global_reaction(emojis: list[str] | None) -> None:
    if emojis:
        await get_database().bot_settings.update_one(
            {"_id": "global_reaction"}, {"$set": {"emojis": emojis}}, upsert=True
        )
    else:
        await get_database().bot_settings.delete_one({"_id": "global_reaction"})


async def global_reaction() -> list[str]:
    setting = await get_database().bot_settings.find_one({"_id": "global_reaction"})
    return list(setting.get("emojis", [])) if setting else []


async def add_global_reaction_ignore(chat_id: int) -> None:
    await get_database().bot_settings.update_one(
        {"_id": "global_reaction_ignores"}, {"$addToSet": {"chat_ids": chat_id}}, upsert=True
    )


async def remove_global_reaction_ignore(chat_id: int) -> bool:
    result = await get_database().bot_settings.update_one(
        {"_id": "global_reaction_ignores"}, {"$pull": {"chat_ids": chat_id}}
    )
    return result.modified_count > 0


async def global_reaction_ignored(chat_id: int) -> bool:
    setting = await get_database().bot_settings.find_one({"_id": "global_reaction_ignores"})
    return chat_id in (setting.get("chat_ids", []) if setting else [])


async def global_reaction_ignores() -> list[int]:
    setting = await get_database().bot_settings.find_one({"_id": "global_reaction_ignores"})
    return list(setting.get("chat_ids", [])) if setting else []


async def set_reaction(chat_id: int, emojis: list[str]) -> None:
    await get_database().reaction_rules.update_one(
        {"_id": chat_id}, {"$set": {"emojis": emojis, "emoji": emojis[0]}}, upsert=True
    )


async def remove_reaction(chat_id: int) -> bool:
    result = await get_database().reaction_rules.delete_one({"_id": chat_id})
    return result.deleted_count == 1


async def reaction_for_chat(chat_id: int) -> str | None:
    rule: dict[str, Any] | None = await get_database().reaction_rules.find_one({"_id": chat_id})
    if not rule:
        return None
    emojis = rule.get("emojis") or ([rule["emoji"]] if rule.get("emoji") else [])
    return random.choice(emojis) if emojis else None


async def list_reactions() -> list[dict[str, Any]]:
    return await get_database().reaction_rules.find().sort("_id", 1).to_list(length=100)
