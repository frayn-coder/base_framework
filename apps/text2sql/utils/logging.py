"""Logging helpers for the Text2SQL service."""
from __future__ import annotations

import logging

from fastapi import Request

from apps.common import get_logger_with_trace


def get_text2sql_logger(request: Request) -> logging.LoggerAdapter:
    from main import t2s_app  # Lazy import to avoid circular references

    return get_logger_with_trace(t2s_app, request)


def get_text2sql_error_logger(request: Request) -> logging.LoggerAdapter:
    from main import t2s_error  # Lazy import to avoid circular references

    return get_logger_with_trace(t2s_error, request)
