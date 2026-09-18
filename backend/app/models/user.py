from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FetchUsersRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)

    @field_validator("user_ids")
    @classmethod
    def positive_and_unique(cls, values: list[int]) -> list[int]:
        if any(value <= 0 for value in values):
            raise ValueError("user_ids must be positive integers")
        return list(dict.fromkeys(values))


class UserOut(BaseModel):
    id: int
    name: str
    email: str | None = None
    username: str | None = None


class ErrorDetail(BaseModel):
    id: int
    reason: Literal["not_found", "provider_error"]


class FetchUsersResponse(BaseModel):
    users: list[UserOut]
    failed: list[int]
    errors: list[ErrorDetail] = []
