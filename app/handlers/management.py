import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin
from app.repositories.stats import get_stats
from app.repositories.settings import set_maintenance
from app.repositories.settings import set_caption_template
from app.repositories.users import add_warning, clear_warnings, get_user, get_user_by_username, get_warnings, list_user_ids, list_users, mark_user_blocked, set_banned, set_user_blocked

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
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
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


@router.message(Command("warn"))
async def warn_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user_id = await _target_user_id(message)
    if user_id is None:
        await message.answer("Usage: /warn <user_id>")
        return
    if is_admin(user_id):
        await message.answer("Configured admins cannot receive warnings.")
        return
    warnings = await add_warning(user_id)
    if warnings >= 3:
        await set_banned(user_id, True)
        await message.answer(f"User {user_id} reached {warnings} warnings and was banned.")
    else:
        await message.answer(f"User {user_id} warned. Warnings: {warnings}/3.")


@router.message(Command("warnings"))
async def warnings_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user_id = await _target_user_id(message)
    if user_id is None:
        await message.answer("Usage: /warnings <user_id>")
        return
    await message.answer(f"User {user_id} has {await get_warnings(user_id)} warning(s).")


@router.message(Command("clearwarnings"))
async def clear_warnings_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user_id = await _target_user_id(message)
    if user_id is None:
        await message.answer("Usage: /clearwarnings <user_id>")
        return
    await clear_warnings(user_id)
    await message.answer(f"Warnings cleared for user {user_id}.")


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


async def _user_reference(message: Message) -> dict | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return await get_user(message.reply_to_message.from_user.id)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        return None
    reference = parts[1].strip()
    try:
        return await get_user(int(reference))
    except ValueError:
        return await get_user_by_username(reference)


@router.message(Command("users"))
async def users_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    users = await list_users()
    if not users:
        await message.answer("No users registered yet.")
        return
    lines = []
    for item in users:
        flags = []
        if item.get("is_premium"):
            flags.append("premium")
        if item.get("is_banned"):
            flags.append("banned")
        if item.get("is_blocked"):
            flags.append("blocked")
        label = "@" + item["username"] if item.get("username") else item.get("first_name", "unknown")
        lines.append(f"{item['_id']} - {label} ({', '.join(flags) or 'active'})")
    await message.answer("Recent users:\n" + "\n".join(lines))


@router.message(Command("finduser"))
async def find_user_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user = await _user_reference(message)
    if user is None:
        await message.answer("User not found. Use /finduser <user_id or @username>.")
        return
    await message.answer(
        f"User: {user['_id']}\nUsername: @{user.get('username') or '-'}\n"
        f"Name: {user.get('first_name') or '-'}\nBlocked: {'yes' if user.get('is_blocked') else 'no'}\n"
        f"Banned: {'yes' if user.get('is_banned') else 'no'}\nWarnings: {user.get('warnings', 0)}"
    )


@router.message(Command("block"))
async def block_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user = await _user_reference(message)
    if user is None:
        await message.answer("Reply to a user or use /block <user_id or @username>.")
        return
    if is_admin(user["_id"]):
        await message.answer("Configured admins cannot be blocked.")
        return
    await set_user_blocked(user["_id"], True)
    await message.answer(f"User {user['_id']} blocked from broadcasts.")


@router.message(Command("unblock"))
async def unblock_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    user = await _user_reference(message)
    if user is None:
        await message.answer("Reply to a user or use /unblock <user_id or @username>.")
        return
    await set_user_blocked(user["_id"], False)
    await message.answer(f"User {user['_id']} unblocked for broadcasts.")


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
