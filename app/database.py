import asyncio
import logging

from pymongo import AsyncMongoClient

from app.config import settings

client: AsyncMongoClient | None = None
database = None
logger = logging.getLogger(__name__)


async def connect_database() -> None:
    global client, database
    last_error: Exception | None = None
    for attempt in range(1, settings.mongo_connect_retries + 1):
        try:
            client = AsyncMongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
            await client.admin.command("ping")
            database = client[settings.mongo_db_name]
            await initialize_indexes()
            logger.info("Connected to MongoDB on attempt %s", attempt)
            return
        except Exception as error:
            last_error = error
            logger.warning("MongoDB connection attempt %s/%s failed: %s", attempt, settings.mongo_connect_retries, error)
            if client is not None:
                await client.close()
                client = None
            database = None
            if attempt < settings.mongo_connect_retries:
                await asyncio.sleep(settings.mongo_retry_delay * attempt)
    raise RuntimeError("Could not connect to MongoDB after retries") from last_error


async def initialize_indexes() -> None:
    db = get_database() if database is not None else None
    if db is None:
        return
    await db.files.create_index([("chat_id", 1), ("message_id", 1)], unique=True)
    await db.files.create_index("normalized_title")
    await db.files.create_index("search_terms")
    await db.force_sub.create_index("title")
    await db.payments.create_index("charge_id", unique=True)
    await db.reaction_rules.create_index("_id", unique=True)
    await db.search_sessions.create_index("expires_at", expireAfterSeconds=0)
    await db.files.create_index("created_at")
    await db.search_stats.create_index("count")
    await db.user_searches.create_index([("user_id", 1), ("last_used_at", -1)])
    await db.file_requests.create_index([("status", 1), ("created_at", 1)])
    await db.saved_files.create_index([("user_id", 1), ("chat_id", 1), ("message_id", 1)], unique=True)
    await db.saved_files.create_index([("user_id", 1), ("created_at", -1)])


async def close_database() -> None:
    global client, database
    if client is not None:
        await client.close()
    client = None
    database = None


async def ping_database() -> bool:
    if client is None:
        return False
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False


def get_database():
    if database is None:
        raise RuntimeError("Database has not been connected")
    return database
