from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("oxyroute.middleware")


def request_logger_middleware(scope: Any, _protocol: Any) -> Any:
    """Pre-route request middleware for OxyRoute 0.4.0.

    Executed before routing and request body parsing.
    Returns ``None`` to allow request processing to continue.
    Returning an HTTP response or dict short-circuits routing.
    """
    method = getattr(scope, "method", "UNKNOWN")
    path = getattr(scope, "path", "/")
    logger.debug("Incoming RSGI request: %s %s", method, path)
    return None
