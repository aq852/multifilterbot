from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.repositories.files import find_files_by_name, get_file
from app.services.deeplinks import build_file_payload

router = Router(name="utility")


@router.message(Command("id"))
async def id_command(message: Message) -> None:
    lines = [f"Your user ID: {message.from_user.id}" if message.from_user else ""]
    if message.chat:
        lines.append(f"Current chat ID: {message.chat.id}")
    if message.reply_to_message and message.reply_to_message.from_user:
        lines.append(f"Replied user ID: {message.reply_to_message.from_user.id}")
    await message.answer("\n".join(lines))


@router.message(Command("info"))
async def info_command(message: Message) -> None:
    target = message.reply_to_message
    if target is None:
        await message.answer("Reply to a document, video, audio, or photo with /info.")
        return
    if target.document:
        media_type, name, size = "document", target.document.file_name or "", target.document.file_size
    elif target.video:
        media_type, name, size = "video", target.video.file_name or "", target.video.file_size
    elif target.audio:
        media_type, name, size = "audio", target.audio.file_name or target.audio.title or "", target.audio.file_size
    elif target.photo:
        media_type, name, size = "photo", "photo", target.photo[-1].file_size
    else:
        await message.answer("The replied message does not contain supported media.")
        return
    size_text = f"{size / 1024 / 1024:.2f} MB" if size else "unknown"
    await message.answer(f"Type: {media_type}\nName: {name or 'untitled'}\nSize: {size_text}")


@router.message(Command("share"))
async def share_command(message: Message) -> None:
    target = message.reply_to_message
    if target is not None:
        chat_id, message_id = target.chat.id, target.message_id
        file = await get_file(chat_id, message_id)
    else:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            await message.answer("Reply to an indexed file or use /share <filename>.")
            return
        matches = await find_files_by_name(parts[1].strip(), limit=5)
        if not matches:
            await message.answer("No indexed file matched that filename.")
            return
        if len(matches) > 1:
            await message.answer("Multiple files matched. Refine the filename or reply to the exact file.")
            return
        file = matches[0]
        chat_id, message_id = file["chat_id"], file["message_id"]
    if file is None:
        await message.answer("That message is not indexed yet.")
        return
    bot_user = await message.bot.get_me()
    if not bot_user.username:
        await message.answer("The bot username is not available for sharing.")
        return
    payload = build_file_payload(chat_id, message_id)
    await message.answer(f"Share this file:\nhttps://t.me/{bot_user.username}?start={payload}")
