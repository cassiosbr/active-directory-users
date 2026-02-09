from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query, Response, status

from api.v1.schemas.users import UserOut
from core.microsoft_graph import (
    GraphNotConfiguredError,
    GraphRequestError,
    get_user_by_email,
    get_user_photo_by_email,
)


router = APIRouter()

@router.get("/users", response_model=list[UserOut])
async def get_users_mock(
    filter: str = Query(
        default="",
        title="Filter",
        description="Filtro para buscar usuários pelo nome ou email.",
    ),
) -> Any:
    """
    Obtém a lista de usuários.

    - **filter**: Filtro para buscar usuários pelo nome ou email.
    """
    # Simulação de dados de usuários
    users = [
        {"name": "Alice", "email": "alice@example.com", "user_principal_name": "alice@example.com", "given_name": "Alice", "surname": "Smith"},
        {"name": "Bob", "email": "bob@example.com", "user_principal_name": "bob@example.com", "given_name": "Bob", "surname": "Johnson"},
        {"name": "Charlie", "email": "charlie@example.com", "user_principal_name": "charlie@example.com", "given_name": "Charlie", "surname": "Brown"}
    ]

    normalized_filter = filter.strip().lower()
    if not normalized_filter:
        return [UserOut(**user) for user in users]
    return [
        UserOut(**user)
        for user in users
        if normalized_filter in (user["name"] or "").lower()
        or normalized_filter in (user["email"] or "").lower()
    ]


@router.get("/users-active-directory", response_model=UserOut)
async def get_users_active_directory(
    email: str = Query(
        ...,
        title="Email",
        description="Email (ou UPN) do usuário no Active Directory.",
        min_length=3,
    ),
) -> Any:
    """
    Obtém um usuário do Active Directory (Microsoft Graph) pelo email/UPN.

    - **email**: Email (ou UPN) do usuário.
    """

    try:
        payload = await get_user_by_email(email)
    except GraphNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.detail,
        )
    except GraphRequestError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    name = payload.get("displayName")
    resolved_email = payload.get("mail") or payload.get("userPrincipalName")
    return UserOut(
        name=name,
        email=resolved_email,
        user_principal_name=payload.get("userPrincipalName"),
        given_name=payload.get("givenName"),
        surname=payload.get("surname"),
    )


@router.get(
    "/users-active-directory-photo",
    response_class=Response,
    responses={200: {"content": {"image/*": {}}}},
)
async def get_users_active_directory_photo(
    email: str = Query(
        ...,
        title="Email",
        description="Email (ou UPN) do usuário no Active Directory.",
        min_length=3,
    ),
) -> Any:    
    """
    Obtém a foto de um usuário do Active Directory (Microsoft Graph) pelo email/UPN.

    - **email**: Email (ou UPN) do usuário.
    """

    try:
        payload = await get_user_photo_by_email(email)
    except GraphNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.detail,
        )
    except GraphRequestError as exc:
        if exc.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Foto não encontrada para o usuário: {email}",
            )
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    return Response(
        content=payload["content"],
        media_type=payload["content_type"],
        status_code=status.HTTP_200_OK,
    )
