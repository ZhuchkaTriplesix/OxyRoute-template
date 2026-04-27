from __future__ import annotations

from typing import Any

from oxyroute import HTTPException
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.redis_client.redis import RedisController
from src.routers.root import dal
from src.routers.root.schemas import ItemCreate, ItemRead, ItemUpdate


async def health_check(
    session_factory: async_sessionmaker[AsyncSession],
    redis: Redis,
) -> dict[str, str]:
    database_status = "ok"
    redis_status = "ok"

    try:
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        database_status = "error"

    try:
        await RedisController.set(redis, "health:probe", "ok", ttl=10)
        await RedisController.get(redis, "health:probe")
    except Exception:
        redis_status = "error"

    status = "ok" if database_status == "ok" and redis_status == "ok" else "error"
    return {"status": status, "database": database_status, "redis": redis_status}


async def list_items(
    session_factory: async_sessionmaker[AsyncSession],
    query: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    limit = int((query or {}).get("limit", 100))
    offset = int((query or {}).get("offset", 0))

    async with session_factory() as session:
        items = await dal.list_items(session, limit=limit, offset=offset)
        return [ItemRead.model_validate(item).model_dump() for item in items]


async def get_item(
    item_id: int,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, Any]:
    async with session_factory() as session:
        item = await dal.get_item(session, item_id)
        if item is None:
            raise HTTPException(404, "item not found")
        return ItemRead.model_validate(item).model_dump()


async def create_item(
    json: dict[str, Any],
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, Any]:
    try:
        payload = ItemCreate.model_validate(json)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors()) from exc

    async with session_factory() as session:
        async with session.begin():
            item = await dal.create_item(session, payload)
        return ItemRead.model_validate(item).model_dump()


async def update_item(
    item_id: int,
    json: dict[str, Any],
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, Any]:
    try:
        payload = ItemUpdate.model_validate(json)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors()) from exc

    async with session_factory() as session:
        async with session.begin():
            item = await dal.get_item(session, item_id)
            if item is None:
                raise HTTPException(404, "item not found")
            updated = await dal.update_item(session, item, payload)
        return ItemRead.model_validate(updated).model_dump()


async def delete_item(
    item_id: int,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, str]:
    async with session_factory() as session:
        async with session.begin():
            item = await dal.get_item(session, item_id)
            if item is None:
                raise HTTPException(404, "item not found")
            await dal.delete_item(session, item)
        return {"status": "deleted"}
