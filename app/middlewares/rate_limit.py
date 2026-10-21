from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from app.access import is_admin
from app.config import settings


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._events: defaultdict[int, deque[float]] = defaultdict(deque)

    def _allowed(self, user_id: int) -> bool:
        now = monotonic()
        events = self._events[user_id]
        while events and now - events[0] >= settings.rate_limit_window:
            events.popleft()
        if len(events) >= settings.rate_limit_burst:
            return False
        events.append(now)
        return True

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user and not is_admin(user.id) and not self._allowed(user.id):
            if isinstance(event, CallbackQuery):
                await event.answer("Too many requests. Please wait a moment.", show_alert=True)
            elif hasattr(event, "answer"):
                await event.answer("Too many requests. Please wait a moment.")
            return None
        return await handler(event, data)
