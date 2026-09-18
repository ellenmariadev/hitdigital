from app.config.settings import Settings
from app.providers.base import UserProvider
from app.providers.fake import FakeUserProvider
from app.providers.jsonplaceholder import JsonPlaceholderUserProvider


def build_provider(settings: Settings) -> UserProvider:
    if settings.user_provider == "fake":
        return FakeUserProvider()
    return JsonPlaceholderUserProvider(settings.provider_base_url, settings.http_timeout)
