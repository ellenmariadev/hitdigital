import random
import time

from app.models.user import UserOut


class InMemoryUserCache:
    def __init__(self, ttl_seconds: int, jitter_seconds: int = 0) -> None:
        self._ttl = ttl_seconds
        self._jitter = jitter_seconds
        self._data: dict[int, tuple[UserOut, float]] = {}

    async def get_many(self, user_ids: list[int]) -> dict[int, UserOut]:
        now = time.monotonic()
        found: dict[int, UserOut] = {}
        for user_id in user_ids:
            entry = self._data.get(user_id)
            if entry is None:
                continue
            user, expires_at = entry
            if expires_at > now:
                found[user_id] = user
            else:
                self._data.pop(user_id, None)
        return found

    async def set_many(self, users: list[UserOut]) -> None:
        ttl: float = self._ttl
        if self._jitter:
            ttl += random.uniform(0, self._jitter)
        expires_at = time.monotonic() + ttl
        for user in users:
            self._data[user.id] = (user, expires_at)
