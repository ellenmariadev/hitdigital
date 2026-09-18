class ProviderError(Exception):
    """Failure while talking to the external provider."""


class UserNotFoundError(ProviderError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"user {user_id} not found")
        self.user_id = user_id
