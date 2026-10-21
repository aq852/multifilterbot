import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

logger = logging.getLogger("multifilterbot.errors")


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception("Unhandled update error")
            try:
                if isinstance(event, CallbackQuery):
                    await event.answer("Something went wrong. Please try again.", show_alert=True)
                elif hasattr(event, "answer"):
                    await event.answer("Something went wrong. Please try again later.")
            except Exception:
                logger.exception("Could not send error response")
            return None
