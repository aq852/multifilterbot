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
    await message.answer("Available commands: /start and /help")
