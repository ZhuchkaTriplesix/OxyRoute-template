from __future__ import annotations

from oxyroute import APIRouter

from src.config import jwt_cfg

secure_router = APIRouter()


@secure_router.get(
    "/me",
    require_jwt=True,
    jwt_secret=jwt_cfg.secret or "change-me",
    algorithms=[jwt_cfg.algorithm],
    jwt_issuer=jwt_cfg.issuer,
    jwt_audience=jwt_cfg.audience,
    jwt_leeway=jwt_cfg.leeway,
)
def me(claims: dict) -> dict:
    return {"sub": claims.get("sub"), "claims": claims}
