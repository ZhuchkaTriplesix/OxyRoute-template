from __future__ import annotations

import contextlib

from oxyroute import App, CORSConfig, SecurityHeadersConfig, apply_cors
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.config import cors_cfg, docs_cfg, postgres_cfg, redis_cfg, security_cfg
from src.configuration.state import set_current_app
from src.database.core import dispose_engine, make_engine, make_session_factory
from src.middlewares import request_logger_middleware
from src.redis_client.redis import close_redis, init_redis
from src.routers import Router


class OxyApp(App):
    def __init__(self) -> None:
        super().__init__(title="OxyRoute Template", include_openapi=docs_cfg.enabled)
        self.state.engine: AsyncEngine | None = None
        self.state.session_factory: async_sessionmaker[AsyncSession] | None = None
        self.state.redis: Redis | None = None
        set_current_app(self)

    async def __rsgi_init__(self, *args, **kwargs) -> None:
        self.state.engine = make_engine(postgres_cfg)
        self.state.session_factory = make_session_factory(self.state.engine)
        self.state.redis = await init_redis(redis_cfg)
        with contextlib.suppress(Exception):
            await self.setup_database(
                postgres_cfg.sqlx_url, max_connections=postgres_cfg.pool_size
            )
        return None

    async def __rsgi_del__(self, *args, **kwargs) -> None:
        with contextlib.suppress(Exception):
            await self.close_database()
        await close_redis(self.state.redis)
        await dispose_engine(self.state.engine)
        self.state.redis = None
        self.state.session_factory = None
        self.state.engine = None
        return None

    def build(self) -> OxyApp:
        self.set_middleware(request_logger_middleware)
        apply_cors(
            self,
            CORSConfig(
                allow_origins=cors_cfg.allow_origins,
                allow_methods=cors_cfg.allow_methods,
                allow_headers=cors_cfg.allow_headers,
                allow_credentials=cors_cfg.allow_credentials,
                max_age=cors_cfg.max_age,
            ),
        )
        self.set_security_headers(
            SecurityHeadersConfig(
                hsts=security_cfg.hsts,
                x_content_type_options=security_cfg.x_content_type_options,
                x_frame_options=security_cfg.x_frame_options,
                referrer_policy=security_cfg.referrer_policy,
                content_security_policy=security_cfg.content_security_policy,
            )
        )

        for entry in Router.routers:
            self.include_router(entry.router, prefix=entry.prefix)

        self.freeze()
        return self
