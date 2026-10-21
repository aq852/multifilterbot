from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.repositories.users import upsert_user
from app.repositories.premium import activate_premium
from app.repositories.users import get_user
from app.services.referrals import parse_referrer
from app.repositories.files import get_file
from app.repositories.discovery import record_file_delivery
from app.services.deeplinks import parse_file_payload
from app.services.subscription import missing_subscriptions, subscription_keyboard
from app.access import is_admin

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message) -> None:
    payload = (message.text or "").split(maxsplit=1)[1] if len((message.text or "").split(maxsplit=1)) == 2 else None
    if message.from_user:
        referrer_id = parse_referrer(payload, message.from_user.id)
        is_new = await upsert_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            referrer_id,
        )
        if is_new and referrer_id and await get_user(referrer_id):
            await activate_premium(
                referrer_id, "referral_bonus", 7, f"referral:{referrer_id}:{message.from_user.id}"
            )
            await activate_premium(
                message.from_user.id, "welcome_bonus", 3, f"welcome:{message.from_user.id}"
            )
    await message.answer(
        "Welcome to MultiFilterBot.\n\n"
        "The bot is ready. Use /search <name> to search indexed files."
    )
    target = parse_file_payload(payload)
    if target and message.from_user:
        chat_id, message_id = target
        if await get_file(chat_id, message_id) is None:
            await message.answer("This shared file is no longer available.")
            return
        missing = await missing_subscriptions(message.bot, message.from_user.id)
        if missing:
            await message.answer(
                "Join the required channels first:",
                reply_markup=subscription_keyboard(missing, f"verify:{chat_id}:{message_id}"),
            )
            return
        await message.bot.copy_message(
            chat_id=message.from_user.id, from_chat_id=chat_id, message_id=message_id,
            protect_content=True,
        )
        await record_file_delivery(chat_id, message_id)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    text = (
        "MultiFilterBot commands\n\n"
        "Search & discovery:\n"
        "/search <name> - search indexed files\n"
        "/latest - recently indexed files\n"
        "/popular - most downloaded files\n"
        "/random - random file\n"
        "/ping - check bot and database status\n"
        "/related <filename> - find similar files\n"
        "/history - your recent searches\n"
        "/clearhistory - clear your search history\n\n"
        "Files & bookmarks:\n"
        "/info <filename> - show file metadata\n"
        "/saved - view saved files\n"
        "/unsave <filename> - remove one saved file\n"
        "/clearsaved - remove all saved files\n"
        "/share <filename> - create a share link\n"
        "/request <filename> - request a missing file\n"
        "/plans, /buy <plan> - Premium plans\n"
        "/myplan, /paymenthistory - Premium status and payments\n"
        "/myrequests - view your open requests\n"
        "/cancelrequest <filename> - cancel your request\n"
    )
    if message.from_user and is_admin(message.from_user.id):
        text += (
            "\nAdmin:\n"
            "/addchannel, /removechannel, /channels\n"
            "/deletefile, /renamefile\n"
            "/stats, /broadcast, /ban, /unban\n"
            "/users, /finduser, /block, /unblock\n"
            "/audit - recent admin activity\n"
            "/maintenance, /setcaption\n"
            "/warn, /warnings, /clearwarnings\n"
            "/autoreactall on <emoji>, /autoreactall off\n"
            "/autoreactignore <chat_id>\n"
            "/welcome on/off\n"
            "/goodbye on/off\n"
            "/setwelcome, /setgoodbye\n"
            "/antiflood, /linkfilter, /modsettings\n"
            "/mute, /unmute\n"
        )
    await message.answer(text)
