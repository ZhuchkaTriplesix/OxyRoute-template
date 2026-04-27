from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from src.config import RedisCfg

DEFAULT_TTL_SECONDS = 3600


async def init_redis(cfg: RedisCfg) -> Redis:
    client = Redis(
        host=cfg.host,
        port=cfg.port,
        db=cfg.db,
        password=cfg.password,
        decode_responses=True,
    )
    await client.ping()
    return client


async def close_redis(client: Redis | None) -> None:
    if client is not None:
        await client.aclose()


class RedisController:
    @staticmethod
    async def get(client: Redis, key: str) -> str | None:
        return await client.get(key)

    @staticmethod
    async def set(
        client: Redis,
        key: str,
        value: str,
        ttl: int | None = DEFAULT_TTL_SECONDS,
    ) -> bool:
        return bool(await client.set(key, value, ex=ttl))

    @staticmethod
    async def delete(client: Redis, key: str) -> int:
        return int(await client.delete(key))

    @staticmethod
    async def delete_many(client: Redis, *keys: str) -> int:
        if not keys:
            return 0
        return int(await client.delete(*keys))

    @staticmethod
    async def get_json(client: Redis, key: str) -> Any | None:
        value = await client.get(key)
        if value is None:
            return None
        return json.loads(value)

    @staticmethod
    async def set_json(
        client: Redis,
        key: str,
        value: Any,
        ttl: int | None = DEFAULT_TTL_SECONDS,
    ) -> bool:
        return bool(await client.set(key, json.dumps(value), ex=ttl))

    @staticmethod
    async def update(
        client: Redis,
        key: str,
        value: str,
        ttl: int | None = DEFAULT_TTL_SECONDS,
    ) -> bool:
        await client.delete(key)
        return await RedisController.set(client, key, value, ttl)

    @staticmethod
    async def exists(client: Redis, key: str) -> bool:
        return bool(await client.exists(key))

    @staticmethod
    async def ttl(client: Redis, key: str) -> int:
        return int(await client.ttl(key))

    @staticmethod
    async def expire(client: Redis, key: str, ttl: int = DEFAULT_TTL_SECONDS) -> bool:
        return bool(await client.expire(key, ttl))
