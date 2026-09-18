import asyncio
from collections.abc import Callable

import httpx
import pytest

from app.config.exceptions import ProviderError, UserNotFoundError
from app.models.user import UserOut
from app.providers.jsonplaceholder import JsonPlaceholderUserProvider

BASE_URL = "https://example.test"
Handler = Callable[[httpx.Request], httpx.Response]


def make_provider(handler: Handler) -> JsonPlaceholderUserProvider:
    client = httpx.AsyncClient(
        base_url=BASE_URL, transport=httpx.MockTransport(handler)
    )
    return JsonPlaceholderUserProvider(BASE_URL, timeout=5.0, client=client)


def test_fetch_user_success() -> None:
    provider = make_provider(
        lambda request: httpx.Response(
            200,
            json={"id": 1, "name": "Leanne Graham", "username": "Bret"},
        )
    )

    async def run() -> None:
        user = await provider.fetch_user(1)
        assert user == UserOut(id=1, name="Leanne Graham", username="Bret")
        await provider.aclose()

    asyncio.run(run())


def test_fetch_user_not_found() -> None:
    provider = make_provider(lambda request: httpx.Response(404))

    async def run() -> None:
        with pytest.raises(UserNotFoundError):
            await provider.fetch_user(1)
        await provider.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("status_code", [302, 400, 500, 503])
def test_fetch_user_http_error(status_code: int) -> None:
    provider = make_provider(lambda request: httpx.Response(status_code))

    async def run() -> None:
        with pytest.raises(ProviderError):
            await provider.fetch_user(1)
        await provider.aclose()

    asyncio.run(run())


def test_fetch_user_invalid_json() -> None:
    provider = make_provider(
        lambda request: httpx.Response(200, content=b"not-json")
    )

    async def run() -> None:
        with pytest.raises(ProviderError):
            await provider.fetch_user(1)
        await provider.aclose()

    asyncio.run(run())


def test_fetch_user_unexpected_shape() -> None:
    provider = make_provider(
        lambda request: httpx.Response(200, json={"id": 1})
    )

    async def run() -> None:
        with pytest.raises(ProviderError):
            await provider.fetch_user(1)
        await provider.aclose()

    asyncio.run(run())
