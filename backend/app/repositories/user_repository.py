from datetime import datetime
from typing import Any, cast

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.models.user import UserOut


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_valid(self, user_ids: list[int], now: datetime) -> list[User]:
        if not user_ids:
            return []
        stmt = select(User).where(User.id.in_(user_ids), User.expires_at > now)
        return list((await self._session.scalars(stmt)).all())

    async def upsert_many(
        self,
        users: list[UserOut],
        *,
        fetched_at: datetime,
        expires_at: datetime,
    ) -> None:
        if not users:
            return

        rows = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "username": user.username,
                "raw": user.model_dump(),
                "fetched_at": fetched_at,
                "expires_at": expires_at,
            }
            for user in users
        ]

        stmt = insert(User).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[User.id],
            set_={
                "name": stmt.excluded.name,
                "email": stmt.excluded.email,
                "username": stmt.excluded.username,
                "raw": stmt.excluded.raw,
                "fetched_at": stmt.excluded.fetched_at,
                "expires_at": stmt.excluded.expires_at,
            },
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def delete_expired(self, now: datetime) -> int:
        result = cast(
            CursorResult[Any],
            await self._session.execute(delete(User).where(User.expires_at <= now)),
        )
        await self._session.commit()
        return result.rowcount or 0
