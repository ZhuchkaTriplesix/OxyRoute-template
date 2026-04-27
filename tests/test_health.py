from __future__ import annotations

from types import TracebackType

import pytest

from src.routers.root.actions import health_check
from src.routers.root.router import version


class FakeSession:
    async def execute(self, query):
        return None


class FakeSessionContext:
    async def __aenter__(self) -> FakeSession:
        return FakeSession()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None


class FakeSessionFactory:
    def __call__(self) -> FakeSessionContext:
        return FakeSessionContext()


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.values[key] = value
        return True

    async def get(self, key: str) -> str | None:
        return self.values.get(key)


@pytest.mark.asyncio
async def test_health_check_with_fake_dependencies() -> None:
    result = await health_check(FakeSessionFactory(), FakeRedis())

    assert result == {"status": "ok", "database": "ok", "redis": "ok"}


def test_version() -> None:
    assert version() == {"name": "oxyroute-template", "version": "0.1.0"}
