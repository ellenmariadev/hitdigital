from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from app.api.users import get_user_service
from app.cache.memory import InMemoryUserCache
from app.config.settings import Settings, get_settings
from app.main import create_app
from app.providers.base import UserProvider
from app.services.user_service import UserService


@pytest.fixture
def settings() -> Settings:
    return Settings(user_provider="fake", cache_backend="memory")


@pytest.fixture
def make_client(settings: Settings):
    @contextmanager
    def _make(provider: UserProvider) -> Iterator[TestClient]:
        app = create_app()
        service = UserService(
            provider=provider,
            cache=InMemoryUserCache(ttl_seconds=60),
        )
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_user_service] = lambda: service
        with TestClient(app) as client:
            yield client

    return _make
