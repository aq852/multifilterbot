from pymongo import AsyncMongoClient

from app.config import settings

client: AsyncMongoClient | None = None
database = None


async def connect_database() -> None:
    global client, database
    client = AsyncMongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
    await client.admin.command("ping")
    database = client[settings.mongo_db_name]


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

