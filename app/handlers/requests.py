from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin
from app.config import settings
from app.repositories.requests import cancel_user_request, close_request, create_request, open_requests, user_open_requests

router = Router(name="requests")


@router.message(Command("request"))
async def request_command(message: Message) -> None:
    if message.from_user is None:
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /request <movie, series, or file name>")
        return
    request_id = await create_request(message.from_user.id, parts[1])
    await message.answer(f"Request received with ID `{request_id}`.", parse_mode="Markdown")
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                f"New file request `{request_id}` from {message.from_user.id}:\n{parts[1].strip()}",
                parse_mode="Markdown",
            )
        except Exception:
            continue


@router.message(Command("requests"))
async def requests_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    requests = await open_requests()
    if not requests:
        await message.answer("No open file requests.")
        return
    lines = [f"{item['_id']} — {item['query']} (user {item['user_id']})" for item in requests]
    await message.answer("Open file requests:\n" + "\n".join(lines))


@router.message(Command("myrequests"))
async def my_requests_command(message: Message) -> None:
    if message.from_user is None:
        return
    requests = await user_open_requests(message.from_user.id)
    if not requests:
        await message.answer("You have no open file requests.")
        return
    lines = [f"- {item['query']} (use /cancelrequest {item['query']})" for item in requests]
    await message.answer("Your open requests:\n" + "\n".join(lines))


@router.message(Command("cancelrequest"))
async def cancel_request_command(message: Message) -> None:
    if message.from_user is None:
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        await message.answer("Usage: /cancelrequest <movie or file name>")
        return
    cancelled = await cancel_user_request(message.from_user.id, parts[1])
    await message.answer("Request cancelled." if cancelled else "Matching open request not found.")


@router.message(Command("closerequest"))
async def close_request_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /closerequest <request_id>")
        return
    closed = await close_request(parts[1].strip(), message.from_user.id)
    await message.answer("Request closed." if closed else "Open request not found.")
