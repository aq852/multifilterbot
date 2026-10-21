from urllib.parse import urlparse
import re

from aiogram import Bot


_MESSAGE_PATH = re.compile(r"^(?P<chat>[^/]+)/(?P<message>\d+)$")
_PRIVATE_MESSAGE_PATH = re.compile(r"^c/(?P<chat>\d+)/(?P<message>\d+)$")


def parse_message_link(value: str) -> tuple[str, int] | None:
    parsed = urlparse(value.strip())
    if parsed.netloc.lower() not in {"t.me", "telegram.me"}:
        return None
    path = parsed.path.strip("/")
    match = _PRIVATE_MESSAGE_PATH.match(path)
    if match:
        return match.group("chat"), int(match.group("message"))
    match = _MESSAGE_PATH.match(path)
    if not match:
        return None
    return match.group("chat"), int(match.group("message"))


async def resolve_message_link(bot: Bot, value: str) -> tuple[int, int] | None:
    parsed = parse_message_link(value)
    if parsed is None:
        return None
    chat_ref, message_id = parsed
    if chat_ref.isdigit():
        chat_id = int(f"-100{chat_ref}")
    else:
        try:
            chat = await bot.get_chat(f"@{chat_ref.lstrip('@')}")
        except Exception:
            return None
        chat_id = chat.id
    return chat_id, message_id
