from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.repositories.users import upsert_user

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message) -> None:
    if message.from_user:
        await upsert_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
    await message.answer(
        "Welcome to MultiFilterBot.\n\n"
        "The bot is ready. Use /search <name> to search indexed files."
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer("Available commands: /start and /help")
