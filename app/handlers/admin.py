from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin

router = Router(name="admin")


@router.message(Command("admin"))
async def admin_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    await message.answer("Admin panel foundation is ready.")
