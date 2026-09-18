from typing import Protocol

from app.models.user import UserOut


class UserCache(Protocol):
    async def get_many(self, user_ids: list[int]) -> dict[int, UserOut]: ...

    async def set_many(self, users: list[UserOut]) -> None: ...
