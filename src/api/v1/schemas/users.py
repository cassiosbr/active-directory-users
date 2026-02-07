from __future__ import annotations

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    name: str | None = Field(default=None, alias="name")
    email: str | None = Field(default=None, alias="email")

    model_config = {
        "populate_by_name": True,
    }
