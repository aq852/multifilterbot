from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from app.access import is_admin
from app.repositories.users import is_banned


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user and not is_admin(user.id) and await is_banned(user.id):
            if isinstance(event, CallbackQuery):
                await event.answer("Your access to this bot has been revoked.", show_alert=True)
            return None
        return await handler(event, data)

