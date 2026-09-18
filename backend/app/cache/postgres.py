import random
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.user import UserOut
from app.repositories.user_repository import UserRepository


class PostgresUserCache:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ttl_seconds: int,
        jitter_seconds: int = 0,
    ) -> None:
        self._session_factory = session_factory
        self._ttl = ttl_seconds
        self._jitter = jitter_seconds

    async def get_many(self, user_ids: list[int]) -> dict[int, UserOut]:
        if not user_ids:
            return {}
        async with self._session_factory() as session:
            rows = await UserRepository(session).get_valid(
                user_ids, datetime.now(UTC)
            )
            return {
                row.id: UserOut(
                    id=row.id,
                    name=row.name,
                    email=row.email,
                    username=row.username,
                )
                for row in rows
            }

    async def set_many(self, users: list[UserOut]) -> None:
        if not users:
            return
        now = datetime.now(UTC)
        ttl: float = self._ttl
        if self._jitter:
            ttl += random.uniform(0, self._jitter)
        async with self._session_factory() as session:
            await UserRepository(session).upsert_many(
                users,
                fetched_at=now,
                expires_at=now + timedelta(seconds=ttl),
            )
