from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.repositories.discovery import latest_files, popular_files, top_searches, user_search_history
from app.repositories.search_sessions import create_search_session
from app.handlers.search import _results_markup

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


@router.message(Command("popular"))
async def popular_command(message: Message) -> None:
    files = await popular_files()
    if not files:
        await message.answer("No file downloads have been recorded yet.")
        return
    buttons = [[InlineKeyboardButton(
        text=f"{index}. {(item.get('title') or item.get('name', 'untitled'))[:48]} ({item.get('downloads', 0)} downloads)",
        callback_data=f"file:{item['chat_id']}:{item['message_id']}",
    )] for index, item in enumerate(files, 1)]
    await message.answer("Most popular files:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.message(Command("history"))
async def history_command(message: Message) -> None:
    if message.from_user is None:
        return
    history = await user_search_history(message.from_user.id)
    if not history:
        await message.answer("Your search history is empty.")
        return
    buttons = [[InlineKeyboardButton(text=item["query"][:60], callback_data=f"history:{index}")]
               for index, item in enumerate(history)]
    await message.answer("Your recent searches:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("history:"))
async def history_callback(callback: CallbackQuery) -> None:
    if callback.message is None:
        return
    try:
        index = int((callback.data or "").split(":", 1)[1])
    except ValueError:
        await callback.answer("Invalid history item.", show_alert=True)
        return
    history = await user_search_history(callback.from_user.id)
    if index < 0 or index >= len(history):
        await callback.answer("That history item has expired.", show_alert=True)
        return
    query = history[index]["query"]
    token = await create_search_session(callback.from_user.id, query)
    text, markup = await _results_markup(query, token, 0)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()
