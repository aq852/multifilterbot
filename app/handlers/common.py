from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.repositories.users import upsert_user
from app.repositories.premium import activate_premium
from app.repositories.users import get_user
from app.services.referrals import parse_referrer

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message) -> None:
    if message.from_user:
        parts = (message.text or "").split(maxsplit=1)
        referrer_id = parse_referrer(parts[1] if len(parts) == 2 else None, message.from_user.id)
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


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer("Available commands: /start and /help")
