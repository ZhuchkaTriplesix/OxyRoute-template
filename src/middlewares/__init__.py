"""OxyRoute 0.4.0 request and response middleware chain."""

from __future__ import annotations

from src.middlewares.request_logger import request_logger_middleware

__all__ = ["request_logger_middleware"]
