from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ACTIVE_DIRECTORY_USERS_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "active-directory-users"
    environment: str = "local"
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"

    api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
