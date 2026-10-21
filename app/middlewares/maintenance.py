from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from app.access import is_admin
from app.repositories.settings import maintenance_enabled


class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user and not is_admin(user.id) and await maintenance_enabled():
            if isinstance(event, CallbackQuery):
                await event.answer("The bot is temporarily under maintenance.", show_alert=True)
            elif hasattr(event, "answer"):
                await event.answer("The bot is temporarily under maintenance. Please try again later.")
            return None
        return await handler(event, data)

