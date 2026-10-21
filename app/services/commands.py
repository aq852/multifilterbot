from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from app.config import settings


USER_COMMANDS = [
    BotCommand(command="start", description="Start the bot"),
    BotCommand(command="help", description="Show available commands"),
    BotCommand(command="profile", description="View your profile"),
    BotCommand(command="search", description="Search indexed files"),
    BotCommand(command="latest", description="Show recent files"),
    BotCommand(command="popular", description="Show popular files"),
    BotCommand(command="random", description="Pick a random file"),
    BotCommand(command="saved", description="View saved files"),
    BotCommand(command="history", description="View search history"),
    BotCommand(command="plans", description="View Premium plans"),
    BotCommand(command="myplan", description="View Premium status"),
    BotCommand(command="request", description="Request a missing file"),
    BotCommand(command="link", description="Create a temporary file link"),
    BotCommand(command="ping", description="Check bot status"),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="admin", description="Open admin dashboard"),
    BotCommand(command="settings", description="Open bot settings"),
    BotCommand(command="audit", description="View admin activity"),
    BotCommand(command="stats", description="View bot statistics"),
    BotCommand(command="broadcast", description="Broadcast a message"),
]


async def configure_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    for admin_id in settings.admin_ids:
        await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id))
