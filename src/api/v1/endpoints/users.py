from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.v1.schemas.users import UserOut
from core.config import settings

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
async def get_users(
    filter: str = Query(
        default="",
        title="Filter",
        description="Filtro para buscar usuários pelo nome ou email.",
    ),
) -> Any:
    """
    Obtém a lista de usuários do Active Directory.

    - **filter**: Filtro para buscar usuários pelo nome ou email.
    """
    # Simulação de dados de usuários
    users = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
        {"name": "Charlie", "email": "charlie@example.com"}
    ]

    return [UserOut(**user) for user in users if filter in user["name"] or filter in user["email"]]