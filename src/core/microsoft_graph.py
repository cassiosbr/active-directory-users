from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
import msal

from core.config import settings


@dataclass(frozen=True)
class GraphNotConfiguredError(RuntimeError):
    detail: str


@dataclass(frozen=True)
class GraphRequestError(RuntimeError):
    status_code: int
    detail: str


_cached_token: str | None = None
_token_expiry: float = 0


def _validate_graph_settings() -> None:
    if not settings.microsoft_graph_tenant_id:
        raise GraphNotConfiguredError(
            "Microsoft Graph não configurado: defina MICROSOFT_GRAPH_TENANT_ID"
        )
    if not settings.microsoft_graph_client_id:
        raise GraphNotConfiguredError(
            "Microsoft Graph não configurado: defina MICROSOFT_GRAPH_CLIENT_ID"
        )
    if not settings.microsoft_graph_client_secret:
        raise GraphNotConfiguredError(
            "Microsoft Graph não configurado: defina MICROSOFT_GRAPH_CLIENT_SECRET"
        )
    if not settings.microsoft_graph_api:    
        raise GraphNotConfiguredError(
            "Microsoft Graph não configurado: defina MICROSOFT_GRAPH_API"
        )
    if not settings.microsoft_graph_scope:
        raise GraphNotConfiguredError(
            "Microsoft Graph não configurado: defina MICROSOFT_GRAPH_SCOPE"
        )
    if not settings.microsoft_graph_authority:
        raise GraphNotConfiguredError(
            "Microsoft Graph não configurado: defina MICROSOFT_GRAPH_AUTHORITY"
        )


def _get_app_token() -> tuple[str, int]:
    _validate_graph_settings()

    authority = f"{settings.microsoft_graph_authority}/{settings.microsoft_graph_tenant_id}"
    app = msal.ConfidentialClientApplication(
        settings.microsoft_graph_client_id,
        authority=authority,
        client_credential=settings.microsoft_graph_client_secret,
    )

    result = app.acquire_token_for_client(scopes=[settings.microsoft_graph_scope])
    if "access_token" in result:
        return result["access_token"], int(result.get("expires_in", 3600))

    raise GraphRequestError(
        status_code=502,
        detail=(
            "Erro obtendo token do Microsoft Graph: "
            f"{result.get('error')}: {result.get('error_description')}"
        ),
    )


def get_cached_token() -> str:
    global _cached_token, _token_expiry

    if not _cached_token or time.time() > _token_expiry:
        token, expires_in = _get_app_token()
        _cached_token = token
        # Folga de 60s para evitar expirar no meio da requisição.
        _token_expiry = time.time() + max(0, int(expires_in) - 60)

    return _cached_token


def clear_token_cache() -> None:
    global _cached_token, _token_expiry
    _cached_token, _token_expiry = None, 0


def _raise_for_graph_response(response: httpx.Response) -> None:
    if response.status_code == 401:
        clear_token_cache()
        raise GraphRequestError(status_code=502, detail="Falha de autenticação no Graph.")

    if response.status_code == 403:
        raise GraphRequestError(
            status_code=403,
            detail="Permissão insuficiente para acessar o Microsoft Graph.",
        )

    if response.status_code == 404:
        raise GraphRequestError(status_code=404, detail="Usuário não encontrado.")

    if response.status_code >= 400:
        raise GraphRequestError(
            status_code=502,
            detail=f"Erro do Microsoft Graph: {response.status_code} - {response.text}",
        )


async def get_user_by_email(email: str) -> dict[str, Any]:
    _validate_graph_settings()

    token = get_cached_token()
    headers = {"Authorization": f"Bearer {token}"}

    graph_api = settings.microsoft_graph_api
    user_key = quote(email.strip())
    url = f"{graph_api}/users/{user_key}"

    params = {
        "$select": (
            "id,displayName,mail,userPrincipalName,"
            "givenName,surname"
        )
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers, params=params)

    _raise_for_graph_response(response)
    return response.json()


async def get_user_photo_by_email(email: str) -> dict[str, Any]:
    _validate_graph_settings()

    token = get_cached_token()
    headers = {"Authorization": f"Bearer {token}"}

    graph_api = settings.microsoft_graph_api
    user_key = quote(email.strip())
    url = f"{graph_api}/users/{user_key}/photos/240x240/$value"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)

    _raise_for_graph_response(response)
    
    
    content_type = response.headers.get("Content-Type", "image/jpeg")
    return {"content": response.content, "content_type": content_type}
