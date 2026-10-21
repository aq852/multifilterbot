import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.access import is_admin
from app.repositories.audit import record_admin_action

logger = logging.getLogger("multifilterbot.audit")


def _action_name(event: Any) -> str | None:
    if isinstance(event, Message):
        text = event.text or event.caption or ""
        if not text.startswith("/"):
            return None
        return text.split(maxsplit=1)[0].split("@", 1)[0][:80]
    if isinstance(event, CallbackQuery) and event.data:
        return f"callback:{event.data[:70]}"
    return None


class AuditMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        result = await handler(event, data)
        user = getattr(event, "from_user", None)
        action = _action_name(event)
        if user and action and is_admin(user.id):
            try:
                await record_admin_action(
                    user_id=user.id,
                    chat_id=getattr(getattr(event, "chat", None), "id", None),
                    action=action,
                    username=user.username,
                )
            except Exception:
                logger.exception("Could not record admin audit action")
        return result
