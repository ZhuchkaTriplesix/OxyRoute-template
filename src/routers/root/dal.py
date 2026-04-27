from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.root.models import Item
from src.routers.root.schemas import ItemCreate, ItemUpdate


async def get_item(session: AsyncSession, item_id: int) -> Item | None:
    return await session.get(Item, item_id)


async def list_items(session: AsyncSession, *, limit: int = 100, offset: int = 0) -> list[Item]:
    result = await session.scalars(select(Item).order_by(Item.id).limit(limit).offset(offset))
    return list(result)


async def create_item(session: AsyncSession, payload: ItemCreate) -> Item:
    item = Item(name=payload.name, description=payload.description)
    session.add(item)
    await session.flush()
    await session.refresh(item)
    return item


async def update_item(session: AsyncSession, item: Item, payload: ItemUpdate) -> Item:
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(item, key, value)
    await session.flush()
    await session.refresh(item)
    return item


async def delete_item(session: AsyncSession, item: Item) -> None:
    await session.delete(item)
