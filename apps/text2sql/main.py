"""Application factory for the Text2SQL service."""
from __future__ import annotations

from fastapi import FastAPI

from .routers import sample
from .utils.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Text2SQL Service")
    register_exception_handlers(app)
    app.include_router(sample.router)
    return app
