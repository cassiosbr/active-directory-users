from __future__ import annotations

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    name: str | None = Field(default=None, alias="name")
    email: str | None = Field(default=None, alias="email")
    user_principal_name: str | None = None
    given_name: str | None = None
    surname: str | None = None

    model_config = {
        "populate_by_name": True,
    }
