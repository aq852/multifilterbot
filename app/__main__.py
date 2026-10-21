import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.database import close_database, connect_database
from app.handlers import admin_router, common_router
from app.health import run_health_server


async def main() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger(__name__)

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN must be configured before starting the bot")

    await connect_database()
    bot = Bot(settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_routers(common_router, admin_router)

    try:
        await asyncio.gather(
            dispatcher.start_polling(bot),
            run_health_server(),
        )
    finally:
        await bot.session.close()
        await close_database()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
