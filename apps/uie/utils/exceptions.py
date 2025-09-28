"""Exception handlers for the UIE service."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .logging import get_uie_error_logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_unhandled_exceptions(request: Request, exc: Exception):  # type: ignore[override]
        logger = get_uie_error_logger(request)
        logger.error("Unhandled exception", exc_info=True)

        trace_id = getattr(request.state, "trace_id", None)
        headers = {"X-Trace-ID": trace_id} if trace_id else {}
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "trace_id": trace_id},
            headers=headers,
        )
