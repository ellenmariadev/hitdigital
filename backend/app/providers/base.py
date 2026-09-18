from typing import Protocol

from app.models.user import UserOut


class UserProvider(Protocol):
    async def fetch_user(self, user_id: int) -> UserOut: ...

    async def aclose(self) -> None: ...
