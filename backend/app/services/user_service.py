import asyncio
import time
from typing import Literal

import structlog

from app.cache.base import UserCache
from app.config.exceptions import UserNotFoundError
from app.models.user import ErrorDetail, FetchUsersResponse, UserOut
from app.providers.base import UserProvider

logger = structlog.get_logger()


class UserService:
    def __init__(self, provider: UserProvider, cache: UserCache) -> None:
        self._provider = provider
        self._cache = cache

    async def fetch_users(self, user_ids: list[int]) -> FetchUsersResponse:
        started = time.perf_counter()

        cached = await self._get_cached(user_ids)
        missing = [user_id for user_id in user_ids if user_id not in cached]

        results = await asyncio.gather(
            *(self._provider.fetch_user(user_id) for user_id in missing),
            return_exceptions=True,
        )

        by_id: dict[int, UserOut] = dict(cached)
        fetched: list[UserOut] = []
        failed: list[int] = []
        errors: list[ErrorDetail] = []

        for user_id, result in zip(missing, results, strict=True):
            if isinstance(result, BaseException):
                reason: Literal["not_found", "provider_error"] = (
                    "not_found"
                    if isinstance(result, UserNotFoundError)
                    else "provider_error"
                )
                failed.append(user_id)
                errors.append(ErrorDetail(id=user_id, reason=reason))
                logger.warning(
                    "user_fetch_failed",
                    user_id=user_id,
                    reason=reason,
                    error=str(result),
                )
            else:
                by_id[user_id] = result
                fetched.append(result)

        await self._set_cached(fetched)

        users = [by_id[user_id] for user_id in user_ids if user_id in by_id]
        logger.info(
            "users_fetched",
            requested=len(user_ids),
            cache_hits=len(cached),
            cache_misses=len(missing),
            success=len(users),
            failed=len(failed),
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        return FetchUsersResponse(users=users, failed=failed, errors=errors)

    async def _get_cached(self, user_ids: list[int]) -> dict[int, UserOut]:
        try:
            return await self._cache.get_many(user_ids)
        except Exception:
            logger.warning("cache_read_failed", exc_info=True)
            return {}

    async def _set_cached(self, users: list[UserOut]) -> None:
        if not users:
            return
        try:
            await self._cache.set_many(users)
        except Exception:
            logger.warning("cache_write_failed", exc_info=True)
