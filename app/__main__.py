import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.database import close_database, connect_database
from app.handlers import admin_router, automation_router, common_router, discovery_router, indexing_router, management_router, payments_router, redeem_router, referrals_router, requests_router, saved_router, search_router, settings_router, utility_router
from app.health import run_health_server
from app.middlewares.ban import BanMiddleware
from app.middlewares.errors import ErrorMiddleware
from app.middlewares.maintenance import MaintenanceMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware


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
    rate_limiter = RateLimitMiddleware()
    error_middleware = ErrorMiddleware()
    dispatcher.message.middleware(error_middleware)
    dispatcher.callback_query.middleware(error_middleware)
    dispatcher.message.middleware(BanMiddleware())
    dispatcher.callback_query.middleware(BanMiddleware())
    dispatcher.message.middleware(MaintenanceMiddleware())
    dispatcher.callback_query.middleware(MaintenanceMiddleware())
    dispatcher.message.middleware(rate_limiter)
    dispatcher.callback_query.middleware(rate_limiter)
    dispatcher.include_routers(common_router, admin_router, indexing_router, search_router, payments_router, redeem_router, management_router, automation_router, referrals_router, discovery_router, utility_router, settings_router, requests_router, saved_router)

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
