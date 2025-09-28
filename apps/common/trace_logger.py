import logging
from fastapi import Request

def get_logger_with_trace(logger: logging.Logger, request: Request) -> logging.LoggerAdapter:
    """返回带 trace_id 的 LoggerAdapter"""
    trace_id = getattr(request.state, "trace_id", None)
    return logging.LoggerAdapter(logger, {"trace_id": trace_id})
