from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.repositories.files import find_files_by_name
from app.repositories.saved_files import clear_saved_files, list_saved_files, remove_saved_file, save_file_for_user

router = Router(name="saved")


def _target(data: str, prefix: str) -> tuple[int, int] | None:
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != prefix:
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None


@router.message(Command("saved"))
async def saved_command(message: Message) -> None:
    if message.from_user is None:
        return
    files = await list_saved_files(message.from_user.id)
    if not files:
        await message.answer("You have no saved files yet. Use Save on a search result.")
        return
    buttons = []
    for item in files:
        title = (item.get("title") or item.get("name", "untitled"))[:55]
        target = f"{item['chat_id']}:{item['message_id']}"
        buttons.append([
            InlineKeyboardButton(text=f"📄 {title}", callback_data=f"file:{target}"),
            InlineKeyboardButton(text="✕", callback_data=f"unsave:{target}"),
        ])
    await message.answer("Your saved files:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.message(Command("unsave"))
async def unsave_command(message: Message) -> None:
    if message.from_user is None:
        return
    target = message.reply_to_message
    if target is not None:
        chat_id, message_id = target.chat.id, target.message_id
    else:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            await message.answer("Reply to a saved file or use /unsave <filename>.")
            return
        matches = await find_files_by_name(parts[1].strip(), limit=5)
        if not matches:
            await message.answer("No indexed file matched that filename.")
            return
        if len(matches) > 1:
            await message.answer("Multiple files matched. Refine the filename or reply to the exact file.")
            return
        chat_id, message_id = matches[0]["chat_id"], matches[0]["message_id"]
    removed = await remove_saved_file(message.from_user.id, chat_id, message_id)
    await message.answer("Removed from saved files." if removed else "That file was not saved.")


@router.message(Command("clearsaved"))
async def clear_saved_command(message: Message) -> None:
    if message.from_user is None:
        return
    deleted = await clear_saved_files(message.from_user.id)
    await message.answer(f"Cleared {deleted} saved file{'s' if deleted != 1 else ''}.")


@router.callback_query(F.data.startswith("save:"))
async def save_callback(callback: CallbackQuery) -> None:
    target = _target(callback.data or "", "save")
    if target is None:
        await callback.answer("Invalid saved file.", show_alert=True)
        return
    await save_file_for_user(callback.from_user.id, *target)
    await callback.answer("File saved.")


@router.callback_query(F.data.startswith("unsave:"))
async def unsave_callback(callback: CallbackQuery) -> None:
    target = _target(callback.data or "", "unsave")
    if target is None:
        await callback.answer("Invalid saved file.", show_alert=True)
        return
    await remove_saved_file(callback.from_user.id, *target)
    await callback.answer("Removed from saved files.")
    if callback.message:
        await callback.message.edit_text("Saved file removed. Use /saved to refresh the list.")
