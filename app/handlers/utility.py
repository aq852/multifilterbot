from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="utility")


@router.message(Command("id"))
async def id_command(message: Message) -> None:
    lines = [f"Your user ID: {message.from_user.id}" if message.from_user else ""]
    if message.chat:
        lines.append(f"Current chat ID: {message.chat.id}")
    if message.reply_to_message and message.reply_to_message.from_user:
        lines.append(f"Replied user ID: {message.reply_to_message.from_user.id}")
    await message.answer("\n".join(lines))

