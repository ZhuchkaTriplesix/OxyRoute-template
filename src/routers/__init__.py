from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from oxyroute import APIRouter

from src.config import docs_cfg
from src.routers.docs.router import docs_router
from src.routers.root.router import root_router
from src.routers.secure.router import secure_router


@dataclass(frozen=True)
class RouterEntry:
    router: APIRouter
    prefix: str
    tags: list[str]


class Router:
    routers: ClassVar[list[RouterEntry]] = [
        RouterEntry(root_router, "/api/root", ["root"]),
        RouterEntry(secure_router, "/api/secure", ["secure"]),
    ]

    if docs_cfg.enabled:
        routers.append(RouterEntry(docs_router, "/api", ["docs"]))
