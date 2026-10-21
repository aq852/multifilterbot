from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.repositories.files import search_files
from app.services.subscription import missing_subscriptions, subscription_keyboard

router = Router(name="search")


@router.message(Command("search"))
async def search_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /search <movie, series, or file name>")
        return
    results = await search_files(parts[1])
    if not results:
        await message.answer("No matching files found.")
        return
    buttons = []
    for item in results:
        title = item.get("title") or item.get("name", "untitled")
        callback_data = f"file:{item['chat_id']}:{item['message_id']}"
        buttons.append([InlineKeyboardButton(text=title[:60], callback_data=callback_data)])
    await message.answer("Search results:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


def _file_target(data: str) -> tuple[int, int] | None:
    parts = data.split(":")
    if len(parts) != 3 or parts[0] not in {"file", "verify"}:
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None


async def _deliver_file(callback: CallbackQuery, chat_id: int, message_id: int) -> None:
    missing = await missing_subscriptions(callback.bot, callback.from_user.id)
    if missing:
        await callback.answer("Join the required channels first.", show_alert=True)
        if callback.message:
            await callback.message.answer(
                "Please join these channels to receive the file:",
                reply_markup=subscription_keyboard(missing, f"verify:{chat_id}:{message_id}"),
            )
        return
    await callback.bot.copy_message(
        chat_id=callback.from_user.id,
        from_chat_id=chat_id,
        message_id=message_id,
        protect_content=True,
    )
    await callback.answer("File sent.")


@router.callback_query(F.data.startswith(("file:", "verify:")))
async def file_callback(callback: CallbackQuery) -> None:
    target = _file_target(callback.data or "")
    if target is None:
        await callback.answer("Invalid file link.", show_alert=True)
        return
    await _deliver_file(callback, *target)
