from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.cache.base import UserCache
from app.cache.memory import InMemoryUserCache
from app.cache.postgres import PostgresUserCache
from app.config.settings import Settings


def build_cache(
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
) -> UserCache:
    if settings.cache_backend == "memory":
        return InMemoryUserCache(
            ttl_seconds=settings.cache_ttl_seconds,
            jitter_seconds=settings.cache_jitter_seconds,
        )
    return PostgresUserCache(
        session_factory=session_factory,
        ttl_seconds=settings.cache_ttl_seconds,
        jitter_seconds=settings.cache_jitter_seconds,
    )
