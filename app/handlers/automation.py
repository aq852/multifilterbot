from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import ChatJoinRequest, Message, ReactionTypeEmoji

from app.access import is_admin
from app.repositories.automation import (
    auto_approve_enabled,
    list_reactions,
    reaction_for_chat,
    remove_reaction,
    set_auto_approve,
    set_reaction,
)

router = Router(name="automation")


def _parse_emojis(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _admin(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


@router.message(Command("autoapprove"))
async def auto_approve_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer("Usage: /autoapprove on or /autoapprove off")
        return
    enabled = parts[1].lower() == "on"
    await set_auto_approve(enabled)
    await message.answer(f"Automatic join-request approval {'enabled' if enabled else 'disabled'}.")


@router.message(Command("autoreact"))
async def auto_react_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) != 3:
        await message.answer("Usage: /autoreact <chat_id> <emoji>[,emoji,...]")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    emojis = _parse_emojis(parts[2])
    if not emojis or len(emojis) > 5 or any(len(emoji) > 8 for emoji in emojis):
        await message.answer("Provide 1 to 5 Telegram emojis separated by commas.")
        return
    await set_reaction(chat_id, emojis)
    await message.answer(f"Automatic reactions {', '.join(emojis)} enabled for {chat_id}.")


@router.message(Command("removeautoreact"))
async def remove_auto_react_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /removeautoreact <chat_id>")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    removed = await remove_reaction(chat_id)
    await message.answer("Automatic reaction removed." if removed else "No reaction rule found.")


@router.message(Command("autoreacts"))
async def auto_reacts_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    rules = await list_reactions()
    if not rules:
        await message.answer("No automatic reaction rules configured.")
        return
    await message.answer("Automatic reactions:\n" + "\n".join(
        f"- {rule['_id']}: {', '.join(rule.get('emojis') or [rule.get('emoji', '')])}" for rule in rules
    ))


@router.chat_join_request()
async def approve_join_request(request: ChatJoinRequest) -> None:
    if not await auto_approve_enabled():
        return
    try:
        await request.bot.approve_chat_join_request(request.chat.id, request.from_user.id)
    except (TelegramBadRequest, TelegramForbiddenError):
        return


@router.channel_post()
async def react_to_channel_post(message: Message) -> None:
    emoji = await reaction_for_chat(message.chat.id)
    if emoji is None:
        return
    try:
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        return
