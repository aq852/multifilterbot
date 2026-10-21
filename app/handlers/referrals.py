from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.repositories.referrals import referral_count

router = Router(name="referrals")


@router.message(Command("refer"))
async def refer_command(message: Message) -> None:
    if message.from_user is None:
        return
    bot_user = await message.bot.get_me()
    count = await referral_count(message.from_user.id)
    await message.answer(
        "Invite friends with this link:\n"
        f"https://t.me/{bot_user.username}?start=ref_{message.from_user.id}\n\n"
        f"Successful referrals: {count}\n"
        "Rewards: 7 Premium days for you and 3 Premium days for each new user."
    )

