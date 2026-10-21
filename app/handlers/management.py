import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin
from app.repositories.stats import get_stats
from app.repositories.users import list_user_ids, mark_user_blocked

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


@router.message(Command("broadcast"))
async def broadcast_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    if message.reply_to_message is None:
        await message.answer("Reply to the message you want to broadcast, then use /broadcast.")
        return
    user_ids = await list_user_ids()
    sent = failed = 0
    for user_id in user_ids:
        try:
            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id,
            )
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
            await mark_user_blocked(user_id)
        await asyncio.sleep(0.05)
    await message.answer(f"Broadcast complete. Sent: {sent}; failed: {failed}.")

