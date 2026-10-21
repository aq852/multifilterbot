from app.database import get_database


async def set_maintenance(enabled: bool) -> None:
    await get_database().bot_settings.update_one(
        {"_id": "maintenance"}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def maintenance_enabled() -> bool:
    setting = await get_database().bot_settings.find_one({"_id": "maintenance"})
    return bool(setting and setting.get("enabled"))

