from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.repositories.subscriptions import list_required_channels


async def missing_subscriptions(bot: Bot, user_id: int) -> list[dict]:
    missing = []
    for channel in await list_required_channels():
        try:
            member = await bot.get_chat_member(channel["_id"], user_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            missing.append(channel)
            continue
        if member.status not in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }:
            missing.append(channel)
    return missing


def subscription_keyboard(channels: list[dict], verify_callback: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"Join {channel['title']}", url=channel["invite_url"])]
        for channel in channels
    ]
    rows.append([InlineKeyboardButton(text="I joined - check again", callback_data=verify_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

