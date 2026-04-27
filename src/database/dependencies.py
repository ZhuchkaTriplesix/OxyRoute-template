from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.configuration.state import get_app_state


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    session_factory = getattr(get_app_state(), "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Database session factory is not initialised")
    return session_factory
