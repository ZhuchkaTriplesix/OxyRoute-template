from __future__ import annotations

from oxyroute import APIRouter, Depends

from src.database.dependencies import get_session_factory
from src.routers.root import actions
from src.routers.root.dependencies import get_redis
from src.routers.root.schemas import ItemCreate, ItemUpdate

root_router = APIRouter()

_db_dep = ("session_factory", Depends(get_session_factory))
_redis_dep = ("redis", Depends(get_redis))


@root_router.get("/health", dependencies=[_db_dep, _redis_dep])
async def health(session_factory, redis) -> dict[str, str]:
    return await actions.health_check(session_factory, redis)


@root_router.get("/version")
def version() -> dict[str, str]:
    return {"name": "oxyroute-template", "version": "0.1.0"}


@root_router.get("/items", dependencies=[_db_dep])
async def list_items(session_factory, query: dict[str, str] | None = None) -> list[dict]:
    return await actions.list_items(session_factory, query)


@root_router.get("/items/:item_id", dependencies=[_db_dep])
async def get_item(item_id: int, session_factory) -> dict:
    return await actions.get_item(item_id, session_factory)


@root_router.post("/items", dependencies=[_db_dep], body_model=ItemCreate)
async def create_item(json: dict, session_factory) -> dict:
    return await actions.create_item(json, session_factory)


@root_router.patch("/items/:item_id", dependencies=[_db_dep], body_model=ItemUpdate)
async def update_item(item_id: int, json: dict, session_factory) -> dict:
    return await actions.update_item(item_id, json, session_factory)


@root_router.delete("/items/:item_id", dependencies=[_db_dep])
async def delete_item(item_id: int, session_factory) -> dict[str, str]:
    return await actions.delete_item(item_id, session_factory)
