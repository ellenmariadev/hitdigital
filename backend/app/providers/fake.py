from app.config.exceptions import UserNotFoundError
from app.models.user import UserOut


class FakeUserProvider:
    def __init__(
        self,
        users: dict[int, UserOut] | None = None,
        *,
        not_found_ids: set[int] | None = None,
    ) -> None:
        self._users = users or {}
        self._not_found = not_found_ids or set()
        self.calls: list[int] = []

    async def fetch_user(self, user_id: int) -> UserOut:
        self.calls.append(user_id)
        if user_id in self._not_found or user_id not in self._users:
            raise UserNotFoundError(user_id)
        return self._users[user_id]

    async def aclose(self) -> None:
        return None
