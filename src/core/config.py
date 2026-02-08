from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Usa caminho absoluto para funcionar independente do CWD.
        env_file=_ENV_FILE,
        # Sem prefixo para suportar ENVIRONMENT, X_API_KEY, MICROSOFT_GRAPH_*.
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "active-directory-users"
    environment: str = "local"
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"

    # Lê a env var X_API_KEY
    x_api_key: str | None = None

    # Microsoft Graph (Client Credentials)
    microsoft_graph_tenant_id: str | None = None
    microsoft_graph_client_id: str | None = None
    microsoft_graph_client_secret: str | None = None
    microsoft_graph_scope: str = "https://graph.microsoft.com/.default"

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
