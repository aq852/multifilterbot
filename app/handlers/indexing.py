from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.access import is_admin
from app.models import file_document
from app.repositories.channels import add_channel, is_indexed_channel, list_channels, remove_channel
from app.repositories.files import delete_file, find_files_by_name, save_file
from app.repositories.subscriptions import add_required_channel, list_required_channels, remove_required_channel

router = Router(name="indexing")


def _admin(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _file_target(message: Message) -> tuple[int, int] | None:
    target = message.reply_to_message
    if target is not None:
        return target.chat.id, target.message_id
    parts = (message.text or "").split()
    if len(parts) != 3:
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None


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
        f"- {channel['title']} ({channel['_id']})" for channel in channels
    ))


@router.message(Command("addfsub"))
async def add_force_sub_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("Usage: /addfsub <chat_id> <invite_url> [display name]")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    title = parts[3] if len(parts) == 4 else str(chat_id)
    await add_required_channel(chat_id, title, parts[2], message.from_user.id)
    await message.answer(f"Force subscription enabled for {title}.")


@router.message(Command("removefsub"))
async def remove_force_sub_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /removefsub <chat_id>")
        return
    try:
        chat_id = int(parts[1])
    except ValueError:
        await message.answer("The chat ID must be a number.")
        return
    removed = await remove_required_channel(chat_id)
    await message.answer("Force subscription removed." if removed else "Channel was not configured.")


@router.message(Command("fsub"))
async def force_sub_list_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    channels = await list_required_channels()
    if not channels:
        await message.answer("No force-subscription channels configured.")
        return
    await message.answer("Force-subscription channels:\n" + "\n".join(
        f"- {channel['title']} ({channel['_id']})" for channel in channels
    ))


@router.message(Command("deletefile"))
async def delete_file_command(message: Message) -> None:
    if not _admin(message):
        await message.answer("You are not authorized to use this command.")
        return
    target = _file_target(message)
    if target is not None:
        removed = await delete_file(*target)
        await message.answer("File removed from the catalog." if removed else "That file is not indexed.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Reply to an indexed file, use /deletefile <chat_id> <message_id>, or pass a filename.")
        return
    matches = await find_files_by_name(parts[1].strip())
    if not matches:
        await message.answer("No indexed file matched that filename.")
        return
    if len(matches) == 1:
        item = matches[0]
        await delete_file(item["chat_id"], item["message_id"])
        await message.answer(f"Removed: {item.get('title') or item.get('name', 'untitled')}")
        return
    buttons = [[InlineKeyboardButton(
        text=(item.get("title") or item.get("name", "untitled"))[:55],
        callback_data=f"admindelete:{item['chat_id']}:{item['message_id']}",
    )] for item in matches]
    await message.answer("Multiple files matched. Choose one to remove:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("admindelete:"))
async def admin_delete_callback(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("You are not authorized.", show_alert=True)
        return
    parts = (callback.data or "").split(":")
    if len(parts) != 3:
        await callback.answer("Invalid file target.", show_alert=True)
        return
    try:
        target = int(parts[1]), int(parts[2])
    except ValueError:
        await callback.answer("Invalid file target.", show_alert=True)
        return
    removed = await delete_file(*target)
    await callback.answer("File removed." if removed else "File was already removed.")
    if callback.message:
        await callback.message.edit_text("File removed from the catalog." if removed else "File was already removed.")


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
