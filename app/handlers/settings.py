import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.access import is_admin
from app.repositories.automation import auto_approve_enabled, list_reactions, set_auto_approve
from app.repositories.channels import list_channels
from app.repositories.settings import maintenance_enabled, set_maintenance
from app.repositories.subscriptions import list_required_channels

router = Router(name="settings")


def _keyboard(maintenance: bool, auto_approve: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"Maintenance: {'ON' if maintenance else 'OFF'}",
            callback_data=f"settings:maintenance:{'off' if maintenance else 'on'}",
        )],
        [InlineKeyboardButton(
            text=f"Auto approve: {'ON' if auto_approve else 'OFF'}",
            callback_data=f"settings:approve:{'off' if auto_approve else 'on'}",
        )],
        [InlineKeyboardButton(text="Refresh", callback_data="settings:refresh")],
    ])


async def _settings_view() -> tuple[str, InlineKeyboardMarkup]:
    maintenance, auto_approve = await asyncio.gather(
        maintenance_enabled(), auto_approve_enabled()
    )
    channels, force_sub, reactions = await asyncio.gather(
        list_channels(), list_required_channels(), list_reactions()
    )
    text = (
        "Bot settings\n\n"
        f"Maintenance: {'ON' if maintenance else 'OFF'}\n"
        f"Auto approval: {'ON' if auto_approve else 'OFF'}\n"
        f"Indexing channels: {len(channels)}\n"
        f"Force-sub channels: {len(force_sub)}\n"
        f"Reaction rules: {len(reactions)}"
    )
    return text, _keyboard(maintenance, auto_approve)


@router.message(Command("settings"))
async def settings_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    text, keyboard = await _settings_view()
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("settings:"))
async def settings_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id) or callback.message is None:
        await callback.answer("Admin access required.", show_alert=True)
        return
    parts = (callback.data or "").split(":")
    if len(parts) == 3 and parts[1] == "maintenance" and parts[2] in {"on", "off"}:
        await set_maintenance(parts[2] == "on")
    elif len(parts) == 3 and parts[1] == "approve" and parts[2] in {"on", "off"}:
        await set_auto_approve(parts[2] == "on")
    text, keyboard = await _settings_view()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("Settings updated.")

