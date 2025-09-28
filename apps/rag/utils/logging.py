"""Logging helpers for the RAG service."""
from __future__ import annotations

import logging

from fastapi import Request

from apps.common import get_logger_with_trace


def get_rag_logger(request: Request) -> logging.LoggerAdapter:
    """Return the project logger enriched with the current trace id."""
    from main import rag_app  # Imported lazily to avoid circular imports

    return get_logger_with_trace(rag_app, request)


def get_rag_error_logger(request: Request) -> logging.LoggerAdapter:
    """Return the error logger enriched with trace context."""
    from main import rag_error  # Imported lazily to avoid circular imports

    return get_logger_with_trace(rag_error, request)
