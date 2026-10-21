from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin
from app.models import file_document
from app.repositories.channels import add_channel, is_indexed_channel, list_channels, remove_channel
from app.repositories.files import save_file

router = Router(name="indexing")


def _admin(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


@router.message(Command("addchannel"))
async def add_channel_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("Usage: /addchannel <chat_id> [display name]")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number, for example -1001234567890.")
        return
    title = parts[2] if len(parts) == 3 else str(chat_id)
    await add_channel(chat_id, title, message.from_user.id)
    await message.answer(f"Indexing enabled for {title} ({chat_id}).")


@router.message(Command("removechannel"))
async def remove_channel_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /removechannel <chat_id>")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    removed = await remove_channel(chat_id)
    await message.answer("Channel removed." if removed else "Channel was not configured.")


@router.message(Command("channels"))
async def channels_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    channels = await list_channels()
    if not channels:
        await message.answer("No indexing channels configured.")
        return
    await message.answer("Configured channels:\n" + "\n".join(
        f"• {channel['title']} ({channel['_id']})" for channel in channels
    ))


async def _index_message(message: Message) -> None:
    if not await is_indexed_channel(message.chat.id):
        return
    if message.document:
        media_type, media, name, size = "document", message.document, message.document.file_name or "", message.document.file_size
    elif message.video:
        media_type, media, name, size = "video", message.video, message.video.file_name or "", message.video.file_size
    elif message.audio:
        media_type, media, name, size = "audio", message.audio, message.audio.file_name or message.audio.title or "", message.audio.file_size
    elif message.photo:
        media_type, media, name, size = "photo", message.photo[-1], "photo", message.photo[-1].file_size
    else:
        return
    await save_file(file_document(
        chat_id=message.chat.id, message_id=message.message_id, media_type=media_type,
        file_id=media.file_id, name=name, size=size, caption=message.caption,
    ))


@router.channel_post()
async def index_channel_post(message: Message) -> None:
    await _index_message(message)

