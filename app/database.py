from pymongo import AsyncMongoClient

from app.config import settings

client: AsyncMongoClient | None = None
database = None


async def connect_database() -> None:
    global client, database
    client = AsyncMongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
    await client.admin.command("ping")
    database = client[settings.mongo_db_name]
    await initialize_indexes()


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


async def close_database() -> None:
    if client is not None:
        await client.close()


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
