from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import settings

router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("admin"))
async def admin_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    await message.answer("Admin panel foundation is ready.")

