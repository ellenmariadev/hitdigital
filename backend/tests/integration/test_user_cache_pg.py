import asyncio
import os
from datetime import UTC, datetime, timedelta

import pytest

from app.db.session import build_engine, build_session_factory
from app.models.user import UserOut
from app.repositories.user_repository import UserRepository

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"), reason="DATABASE_URL is not set"
)


def test_upsert_read_and_delete_expired() -> None:
    async def run() -> None:
        engine = build_engine()
        factory = build_session_factory(engine)
        now = datetime.now(UTC)
        user = UserOut(id=99, name="Cache User", email="cache@example.com")
        try:
            async with factory() as session:
                await UserRepository(session).upsert_many(
                    [user],
                    fetched_at=now,
                    expires_at=now + timedelta(seconds=60),
                )

            async with factory() as session:
                rows = await UserRepository(session).get_valid([99], now)
                assert [row.id for row in rows] == [99]
                assert rows[0].name == "Cache User"

            async with factory() as session:
                removed = await UserRepository(session).delete_expired(
                    now + timedelta(seconds=120)
                )
                assert removed >= 1
        finally:
            await engine.dispose()

    asyncio.run(run())
