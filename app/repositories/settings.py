from app.database import get_database


async def set_maintenance(enabled: bool) -> None:
    await get_database().bot_settings.update_one(
        {"_id": "maintenance"}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def maintenance_enabled() -> bool:
    setting = await get_database().bot_settings.find_one({"_id": "maintenance"})
    return bool(setting and setting.get("enabled"))


async def set_caption_template(template: str | None) -> None:
    if template:
        await get_database().bot_settings.update_one(
            {"_id": "caption_template"}, {"$set": {"value": template}}, upsert=True
        )
    else:
        await get_database().bot_settings.delete_one({"_id": "caption_template"})


async def caption_template() -> str | None:
    setting = await get_database().bot_settings.find_one({"_id": "caption_template"})
    return setting.get("value") if setting else None
