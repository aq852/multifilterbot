from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.repositories.files import search_files

router = Router(name="search")


@router.message(Command("search"))
async def search_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /search <movie, series, or file name>")
        return
    results = await search_files(parts[1])
    if not results:
        await message.answer("No matching files found.")
        return
    lines = [f"{index}. {item.get('title') or item.get('name', 'untitled')}"
             for index, item in enumerate(results, 1)]
    await message.answer("Search results:\n" + "\n".join(lines))

