from __future__ import annotations

from fastapi import FastAPI

from api.v1.router import api_router
from core.config import settings
from core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
