from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import PostgresCfg


def make_engine(cfg: PostgresCfg) -> AsyncEngine:
    return create_async_engine(
        cfg.url,
        echo=cfg.echo,
        pool_timeout=cfg.pool_timeout,
        pool_recycle=cfg.pool_recycle,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_pre_ping=cfg.pool_pre_ping,
    )


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def dispose_engine(engine: AsyncEngine | None) -> None:
    if engine is not None:
        await engine.dispose()


async def session_scope(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session, session.begin():
        yield session
