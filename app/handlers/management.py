import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin
from app.repositories.stats import get_stats
from app.repositories.settings import set_maintenance
from app.repositories.settings import set_caption_template
from app.repositories.users import get_user, list_user_ids, mark_user_blocked, set_banned

router = Router(name="management")


def _admin(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


@router.message(Command("stats"))
async def stats_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    stats = await get_stats()
    await message.answer(
        "Bot statistics:\n"
        f"Users: {stats['users']}\n"
        f"Indexed files: {stats['files']}\n"
        f"Configured channels: {stats['channels']}\n"
        f"Active Premium users: {stats['premium']}"
    )


async def _target_user_id(message: Message) -> int | None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


@router.message(Command("ban"))
async def ban_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user_id = await _target_user_id(message)
    if user_id is None:
        await message.answer("Usage: /ban <user_id>")
        return
    if is_admin(user_id):
        await message.answer("Configured admins cannot be banned.")
        return
    await set_banned(user_id, True)
    await message.answer(f"User {user_id} has been banned.")


@router.message(Command("unban"))
async def unban_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user_id = await _target_user_id(message)
    if user_id is None:
        await message.answer("Usage: /unban <user_id>")
        return
    await set_banned(user_id, False)
    await message.answer(f"User {user_id} has been unbanned.")


@router.message(Command("user"))
async def user_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user_id = await _target_user_id(message)
    if user_id is None:
        await message.answer("Usage: /user <user_id>")
        return
    user = await get_user(user_id)
    if user is None:
        await message.answer("User not found.")
        return
    await message.answer(
        f"User: {user_id}\n"
        f"Username: @{user.get('username') or '-'}\n"
        f"Premium: {'yes' if user.get('is_premium') else 'no'}\n"
        f"Banned: {'yes' if user.get('is_banned') else 'no'}"
    )


@router.message(Command("maintenance"))
async def maintenance_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer("Usage: /maintenance on or /maintenance off")
        return
    enabled = parts[1].lower() == "on"
    await set_maintenance(enabled)
    await message.answer(f"Maintenance mode {'enabled' if enabled else 'disabled'}.")


@router.message(Command("setcaption"))
async def set_caption_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /setcaption <template>\nPlaceholders: {title}, {name}, {type}, {size}")
        return
    await set_caption_template(parts[1].strip())
    await message.answer("Delivery caption template saved.")


@router.message(Command("clearcaption"))
async def clear_caption_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    await set_caption_template(None)
    await message.answer("Delivery caption template cleared.")


@router.message(Command("broadcast"))
async def broadcast_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    if message.reply_to_message is None:
        await message.answer("Reply to the message you want to broadcast, then use /broadcast.")
        return
    user_ids = await list_user_ids()
    sent = failed = blocked = 0
    for user_id in user_ids:
        try:
            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id,
            )
            sent += 1
        except TelegramForbiddenError:
            blocked += 1
            failed += 1
            await mark_user_blocked(user_id)
        except TelegramBadRequest:
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await message.answer(
        f"Broadcast complete.\nSent: {sent}\nFailed: {failed}\nBlocked users: {blocked}"
    )
