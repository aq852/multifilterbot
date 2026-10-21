from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

from app.access import is_admin
from app.database import ping_database
from app.repositories.channels import list_channels
from app.repositories.requests import open_requests
from app.repositories.stats import get_stats
from app.repositories.settings import maintenance_enabled
from app.repositories.subscriptions import list_required_channels
from app.repositories.audit import list_admin_actions

router = Router(name="admin")


@router.message(Command("admin"))
async def admin_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    stats, channels, force_sub, requests, database_ok, maintenance = await asyncio.gather(
        get_stats(), list_channels(), list_required_channels(), open_requests(),
        ping_database(), maintenance_enabled(),
    )
    await message.answer(
        "Admin dashboard\n\n"
        f"Database: {'online' if database_ok else 'offline'}\n"
        f"Maintenance: {'on' if maintenance else 'off'}\n"
        f"Users: {stats['users']}\n"
        f"Indexed files: {stats['files']}\n"
        f"Premium users: {stats['premium']}\n"
        f"Indexing channels: {len(channels)}\n"
        f"Force-sub channels: {len(force_sub)}\n"
        f"Open requests: {len(requests)}"
    )


@router.message(Command("audit"))
async def audit_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    logs = await list_admin_actions()
    if not logs:
        await message.answer("No admin activity has been recorded yet.")
        return
    lines = ["Recent admin activity:"]
    for item in logs:
        created = item.get("created_at")
        timestamp = created.astimezone().strftime("%Y-%m-%d %H:%M") if created else "unknown time"
        actor = f"@{item['username']}" if item.get("username") else str(item.get("user_id"))
        lines.append(f"• {timestamp} — {actor} — {item.get('action', 'unknown')}")
    await message.answer("\n".join(lines))
