import random

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import ChatJoinRequest, Message, ReactionTypeEmoji

from app.access import is_admin
from app.repositories.automation import (
    auto_approve_enabled,
    add_global_reaction_ignore,
    global_reaction,
    global_reaction_ignored, global_reaction_ignores,
    member_message_template,
    list_reactions,
    reaction_for_chat,
    remove_reaction,
    set_auto_approve,
    set_global_reaction,
    set_reaction,
    set_goodbye,
    set_member_message,
    set_welcome,
    welcome_enabled,
    goodbye_enabled,
    remove_global_reaction_ignore,
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


@router.message(Command("welcome"))
async def welcome_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer("Usage: /welcome on or /welcome off")
        return
    enabled = parts[1].lower() == "on"
    await set_welcome(message.chat.id, enabled)
    await message.answer(f"Welcome messages {'enabled' if enabled else 'disabled'} for this chat.")


@router.message(Command("goodbye"))
async def goodbye_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer("Usage: /goodbye on or /goodbye off")
        return
    enabled = parts[1].lower() == "on"
    await set_goodbye(message.chat.id, enabled)
    await message.answer(f"Goodbye messages {'enabled' if enabled else 'disabled'} for this chat.")


@router.message(Command("setwelcome"))
async def set_welcome_message_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /setwelcome Welcome, {name}!\nUse /clearwelcome to restore the default.")
        return
    await set_member_message(message.chat.id, "welcome", parts[1].strip())
    await message.answer("Custom welcome message saved.")


@router.message(Command("clearwelcome"))
async def clear_welcome_message_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    await set_member_message(message.chat.id, "welcome", None)
    await message.answer("Custom welcome message cleared.")


@router.message(Command("setgoodbye"))
async def set_goodbye_message_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /setgoodbye Goodbye, {name}!\nUse /cleargoodbye to restore the default.")
        return
    await set_member_message(message.chat.id, "goodbye", parts[1].strip())
    await message.answer("Custom goodbye message saved.")


@router.message(Command("cleargoodbye"))
async def clear_goodbye_message_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    await set_member_message(message.chat.id, "goodbye", None)
    await message.answer("Custom goodbye message cleared.")


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


@router.message(Command("autoreactall"))
async def global_auto_react_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer("Usage: /autoreactall on <emoji>[,emoji,...] or /autoreactall off")
        return
    if parts[1].lower() == "off":
        await set_global_reaction(None)
        await message.answer("Global automatic reactions disabled.")
        return
    emojis = _parse_emojis(parts[2]) if len(parts) == 3 else []
    if not emojis or len(emojis) > 5 or any(len(emoji) > 8 for emoji in emojis):
        await message.answer("Provide 1 to 5 Telegram emojis separated by commas.")
        return
    await set_global_reaction(emojis)
    await message.answer(f"Global automatic reactions enabled: {', '.join(emojis)}")


@router.message(Command("autoreactignore"))
async def ignore_auto_react_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /autoreactignore <chat_id>")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    await add_global_reaction_ignore(chat_id)
    await message.answer(f"Global reactions disabled for {chat_id}.")


@router.message(Command("removeautoreactignore"))
async def remove_ignore_auto_react_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /removeautoreactignore <chat_id>")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    removed = await remove_global_reaction_ignore(chat_id)
    await message.answer("Global reaction ignore removed." if removed else "Chat was not ignored.")


@router.message(Command("autoreactignores"))
async def list_ignore_auto_react_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    ignores = await global_reaction_ignores()
    await message.answer("Ignored chats:\n" + ("\n".join(map(str, ignores)) if ignores else "None"))


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


@router.message(F.new_chat_members)
async def welcome_new_members(message: Message) -> None:
    if not await welcome_enabled(message.chat.id):
        return
    names = ", ".join(member.full_name for member in message.new_chat_members)
    template = await member_message_template(message.chat.id, "welcome")
    await message.answer((template or "Welcome, {name}! Please read the group rules and enjoy your stay.").replace("{name}", names))


@router.message(F.left_chat_member)
async def goodbye_member(message: Message) -> None:
    if not await goodbye_enabled(message.chat.id) or message.left_chat_member is None:
        return
    template = await member_message_template(message.chat.id, "goodbye")
    await message.answer((template or "Goodbye, {name}! Take care.").replace("{name}", message.left_chat_member.full_name))
    try:
        await request.bot.approve_chat_join_request(request.chat.id, request.from_user.id)
    except (TelegramBadRequest, TelegramForbiddenError):
        return


@router.channel_post()
async def react_to_channel_post(message: Message) -> None:
    emoji = await reaction_for_chat(message.chat.id)
    if emoji is None and not await global_reaction_ignored(message.chat.id):
        emojis = await global_reaction()
        emoji = random.choice(emojis) if emojis else None
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


@router.message()
async def react_to_any_message(message: Message) -> None:
    """React in private chats/groups where Telegram delivers message updates."""
    emoji = await reaction_for_chat(message.chat.id)
    if emoji is None and not await global_reaction_ignored(message.chat.id):
        emojis = await global_reaction()
        emoji = random.choice(emojis) if emojis else None
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
