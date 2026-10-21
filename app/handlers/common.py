from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Welcome to MultiFilterBot.\n\n"
        "The bot foundation is ready. Search and media indexing modules will be added next."
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer("Available commands: /start and /help")
