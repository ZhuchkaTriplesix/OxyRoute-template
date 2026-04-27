from __future__ import annotations

from redis.asyncio import Redis

from src.configuration.state import get_app_state


def get_redis() -> Redis:
    redis = getattr(get_app_state(), "redis", None)
    if redis is None:
        raise RuntimeError("Redis client is not initialised")
    return redis
