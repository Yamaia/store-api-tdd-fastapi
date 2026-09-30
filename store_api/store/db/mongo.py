from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from store.core.config import settings


@lru_cache
def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.database_url, tz_aware=True)


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.database_name]
