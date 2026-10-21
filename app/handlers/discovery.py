from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.repositories.discovery import latest_files, top_searches

router = Router(name="discovery")


@router.message(Command("latest"))
async def latest_command(message: Message) -> None:
    files = await latest_files()
    if not files:
        await message.answer("No files have been indexed yet.")
        return
    buttons = [[InlineKeyboardButton(
        text=(item.get("title") or item.get("name", "untitled"))[:60],
        callback_data=f"file:{item['chat_id']}:{item['message_id']}",
    )] for item in files]
    await message.answer("Recently indexed files:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.message(Command("top"))
async def top_command(message: Message) -> None:
    searches = await top_searches()
    if not searches:
        await message.answer("No searches recorded yet.")
        return
    lines = [f"{index}. {item['query']} — {item['count']} searches"
             for index, item in enumerate(searches, 1)]
    await message.answer("Top searches:\n" + "\n".join(lines))

