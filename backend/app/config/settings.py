import json
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "hitdigital-backend"
    debug: bool = False
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    database_url: str
    db_echo: bool = False
    db_pool_size: int = Field(default=5, gt=0)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_recycle_seconds: int = Field(default=1800, gt=0)

    user_provider: Literal["jsonplaceholder", "fake"] = "jsonplaceholder"
    provider_base_url: str = "https://jsonplaceholder.typicode.com"
    http_timeout: float = Field(default=5.0, gt=0)
    max_user_ids: int = Field(default=500, gt=0)

    cache_backend: Literal["postgres", "memory"] = "postgres"
    cache_ttl_seconds: int = Field(default=300, gt=0)
    cache_jitter_seconds: int = Field(default=30, ge=0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, values: object) -> object:
        if isinstance(values, str):
            text = values.strip()
            if text.startswith("["):
                return json.loads(text)
            return [origin.strip() for origin in text.split(",") if origin.strip()]
        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()
