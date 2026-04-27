from __future__ import annotations

from oxyroute import HTTPException

from src.config import docs_cfg
from src.misc.security import basic_auth_matches

_WWW_AUTHENTICATE = 'Basic realm="OxyRoute docs", charset="UTF-8"'


def basic_auth_guard(request: dict) -> str:
    headers = request.get("headers") or {}
    authorization = headers.get("authorization") or headers.get("Authorization")

    if basic_auth_matches(authorization, docs_cfg.username, docs_cfg.password):
        return docs_cfg.username

    raise HTTPException(
        401,
        "authentication required",
        headers={"WWW-Authenticate": _WWW_AUTHENTICATE},
    )
