import httpx
from pydantic import ValidationError

from app.config.exceptions import ProviderError, UserNotFoundError
from app.models.user import UserOut


class JsonPlaceholderUserProvider:
    def __init__(
        self,
        base_url: str,
        timeout: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client or httpx.AsyncClient(
            base_url=base_url, timeout=timeout
        )

    async def fetch_user(self, user_id: int) -> UserOut:
        try:
            response = await self._client.get(f"/users/{user_id}")
        except httpx.HTTPError as exc:
            raise ProviderError(str(exc)) from exc

        if response.status_code == 404:
            raise UserNotFoundError(user_id)
        if not response.is_success:
            raise ProviderError(f"HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderError("invalid JSON response") from exc

        try:
            return UserOut(
                id=data["id"],
                name=data["name"],
                email=data.get("email"),
                username=data.get("username"),
            )
        except (KeyError, TypeError, ValidationError) as exc:
            raise ProviderError("unexpected response shape") from exc

    async def aclose(self) -> None:
        await self._client.aclose()
