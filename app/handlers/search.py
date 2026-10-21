from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.repositories.files import count_search_files, get_file, search_files
from app.repositories.search_sessions import create_search_session, get_search_session
from app.repositories.discovery import record_search
from app.services.search import parse_media_filter
from app.services.subscription import missing_subscriptions, subscription_keyboard
from app.services.captions import render_caption
from app.repositories.settings import caption_template

router = Router(name="search")
PAGE_SIZE = 5


def _file_target(data: str) -> tuple[int, int] | None:
    parts = data.split(":")
    if len(parts) != 3 or parts[0] not in {"file", "verify"}:
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None


def _page_target(data: str) -> tuple[str, int] | None:
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "search":
        return None
    try:
        page = int(parts[2])
    except ValueError:
        return None
    if page < 0:
        return None
    return parts[1], page


async def _results_markup(query: str, token: str, page: int) -> tuple[str, InlineKeyboardMarkup | None]:
    total = await count_search_files(query)
    filtered_query, media_type = parse_media_filter(query)
    results = await search_files(filtered_query, limit=PAGE_SIZE, skip=page * PAGE_SIZE, media_type=media_type)
    if not results:
        return "No matching files found.", None
    buttons = [[InlineKeyboardButton(
        text=(item.get("title") or item.get("name", "untitled"))[:60],
        callback_data=f"file:{item['chat_id']}:{item['message_id']}",
    )] for item in results]
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"search:{token}:{page - 1}"))
    if (page + 1) * PAGE_SIZE < total:
        navigation.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"search:{token}:{page + 1}"))
    if navigation:
        buttons.append(navigation)
    label = f"{media_type}: {filtered_query}" if media_type else filtered_query
    return f"Search results for: {label}\nPage {page + 1} of {(total + PAGE_SIZE - 1) // PAGE_SIZE}", InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("search"))
async def search_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip() or message.from_user is None:
        await message.answer("Usage: /search <name> or /search video:<name>")
        return
    query = parts[1].strip()
    await record_search(query)
    token = await create_search_session(message.from_user.id, query)
    text, markup = await _results_markup(query, token, 0)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("search:"))
async def search_page_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None or callback.message is None:
        return
    target = _page_target(callback.data or "")
    if target is None:
        await callback.answer("Invalid search page.", show_alert=True)
        return
    token, page = target
    if page is None:
        await callback.answer("Invalid search page.", show_alert=True)
        return
    session = await get_search_session(token, callback.from_user.id)
    if session is None:
        await callback.answer("This search has expired. Search again.", show_alert=True)
        return
    text, markup = await _results_markup(session["query"], token, page)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


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
    file = await get_file(chat_id, message_id)
    template = await caption_template()
    caption = render_caption(template, file) if template and file else None
    await callback.bot.copy_message(
        chat_id=callback.from_user.id, from_chat_id=chat_id, message_id=message_id,
        caption=caption, protect_content=True,
    )
    await callback.answer("File sent.")


@router.callback_query(F.data.startswith(("file:", "verify:")))
async def file_callback(callback: CallbackQuery) -> None:
    target = _file_target(callback.data or "")
    if target is None:
        await callback.answer("Invalid file link.", show_alert=True)
        return
    await _deliver_file(callback, *target)
