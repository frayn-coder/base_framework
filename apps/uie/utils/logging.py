"""Logging helpers for the UIE service."""
from __future__ import annotations

import logging

from fastapi import Request

from apps.common import get_logger_with_trace


def get_uie_logger(request: Request) -> logging.LoggerAdapter:
    from main import uie_app  # Lazy import to avoid circular dependencies

    return get_logger_with_trace(uie_app, request)


def get_uie_error_logger(request: Request) -> logging.LoggerAdapter:
    from main import uie_error  # Lazy import to avoid circular dependencies

    return get_logger_with_trace(uie_error, request)
