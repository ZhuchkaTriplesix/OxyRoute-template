from __future__ import annotations

import os
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(os.getenv("OXYROUTE_CONFIG", BASE_DIR / "config.ini"))

config = ConfigParser()
config.read(CONFIG_PATH)


def _get(section: str, key: str, fallback: str = "") -> str:
    return os.getenv(f"{section}_{key}", config.get(section, key, fallback=fallback)).strip()


def _get_bool(section: str, key: str, fallback: bool = False) -> bool:
    value = _get(section, key, str(fallback)).lower()
    return value in {"1", "true", "yes", "on"}


def _get_int(section: str, key: str, fallback: int) -> int:
    return int(_get(section, key, str(fallback)))


def _csv(section: str, key: str, fallback: str = "") -> list[str]:
    return [item.strip() for item in _get(section, key, fallback).split(",") if item.strip()]


@dataclass(frozen=True)
class PostgresCfg:
    database: str = field(default_factory=lambda: _get("POSTGRES", "DATABASE", "postgresql"))
    driver: str = field(default_factory=lambda: _get("POSTGRES", "DRIVER", "asyncpg"))
    database_name: str = field(
        default_factory=lambda: _get("POSTGRES", "DATABASE_NAME", "oxyroute_db")
    )
    username: str = field(default_factory=lambda: _get("POSTGRES", "USERNAME", "postgres"))
    password: str = field(default_factory=lambda: _get("POSTGRES", "PASSWORD", "postgres"))
    ip: str = field(
        default_factory=lambda: os.getenv("POSTGRES_IP", _get("POSTGRES", "IP", "localhost"))
    )
    port: int = field(
        default_factory=lambda: int(
            os.getenv("POSTGRES_INTERNAL_PORT", _get("POSTGRES", "PORT", "5432"))
        )
    )
    pool_timeout: int = field(
        default_factory=lambda: _get_int("POSTGRES", "DATABASE_ENGINE_POOL_TIMEOUT", 30)
    )
    pool_recycle: int = field(
        default_factory=lambda: _get_int("POSTGRES", "DATABASE_ENGINE_POOL_RECYCLE", 3600)
    )
    pool_size: int = field(
        default_factory=lambda: _get_int("POSTGRES", "DATABASE_ENGINE_POOL_SIZE", 5)
    )
    max_overflow: int = field(
        default_factory=lambda: _get_int("POSTGRES", "DATABASE_ENGINE_MAX_OVERFLOW", 10)
    )
    pool_pre_ping: bool = field(
        default_factory=lambda: _get_bool("POSTGRES", "DATABASE_ENGINE_POOL_PING", True)
    )
    echo: bool = field(default_factory=lambda: _get_bool("POSTGRES", "DATABASE_ECHO", False))

    @property
    def url(self) -> str:
        return (
            f"{self.database}+{self.driver}://{self.username}:{self.password}"
            f"@{self.ip}:{self.port}/{self.database_name}"
        )

    @property
    def sqlx_url(self) -> str:
        return (
            f"{self.database}://{self.username}:{self.password}"
            f"@{self.ip}:{self.port}/{self.database_name}"
        )


@dataclass(frozen=True)
class GranianCfg:
    host: str = field(
        default_factory=lambda: os.getenv("GRANIAN_HOST", _get("GRANIAN", "HOST", "0.0.0.0"))
    )
    port: int = field(default_factory=lambda: _get_int("GRANIAN", "PORT", 8000))
    workers: int = field(default_factory=lambda: _get_int("GRANIAN", "WORKERS", 2))
    loop: str = field(default_factory=lambda: _get("GRANIAN", "LOOP", "uvloop"))
    http: str = field(default_factory=lambda: _get("GRANIAN", "HTTP", "auto"))


@dataclass(frozen=True)
class RedisCfg:
    host: str = field(
        default_factory=lambda: os.getenv("REDIS_HOST", _get("REDIS", "HOST", "localhost"))
    )
    port: int = field(
        default_factory=lambda: int(os.getenv("REDIS_INTERNAL_PORT", _get("REDIS", "PORT", "6379")))
    )
    db: int = field(default_factory=lambda: _get_int("REDIS", "DB", 0))
    password: str | None = field(default_factory=lambda: _get("REDIS", "PASSWORD", "") or None)


@dataclass(frozen=True)
class DocsCfg:
    enabled: bool = field(default_factory=lambda: _get_bool("DOCS", "ENABLED", True))
    username: str = field(default_factory=lambda: _get("DOCS", "USERNAME", "admin"))
    password: str = field(default_factory=lambda: _get("DOCS", "PASSWORD", "change_me"))


@dataclass(frozen=True)
class CorsCfg:
    allow_origins: list[str] = field(default_factory=lambda: _csv("CORS", "ALLOW_ORIGINS", "*"))
    allow_methods: list[str] = field(
        default_factory=lambda: _csv("CORS", "ALLOW_METHODS", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
    )
    allow_headers: list[str] = field(
        default_factory=lambda: _csv("CORS", "ALLOW_HEADERS", "authorization,content-type")
    )
    allow_credentials: bool = field(
        default_factory=lambda: _get_bool("CORS", "ALLOW_CREDENTIALS", False)
    )
    max_age: int | None = field(default_factory=lambda: _get_int("CORS", "MAX_AGE", 600))


@dataclass(frozen=True)
class SecurityCfg:
    hsts: str | None = field(default_factory=lambda: _get("SECURITY", "HSTS", "") or None)
    content_security_policy: str | None = field(
        default_factory=lambda: (
            _get("SECURITY", "CONTENT_SECURITY_POLICY", "default-src 'self'") or None
        )
    )
    referrer_policy: str | None = field(
        default_factory=lambda: (
            _get("SECURITY", "REFERRER_POLICY", "strict-origin-when-cross-origin") or None
        )
    )
    x_frame_options: str | None = field(
        default_factory=lambda: _get("SECURITY", "X_FRAME_OPTIONS", "DENY") or None
    )
    x_content_type_options: str | None = field(
        default_factory=lambda: _get("SECURITY", "X_CONTENT_TYPE_OPTIONS", "nosniff") or None
    )


@dataclass(frozen=True)
class JwtCfg:
    secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", _get("JWT", "SECRET", "")))
    algorithm: str = field(default_factory=lambda: _get("JWT", "ALGORITHM", "HS256"))
    issuer: str | None = field(default_factory=lambda: _get("JWT", "ISSUER", "") or None)
    audience: str | None = field(default_factory=lambda: _get("JWT", "AUDIENCE", "") or None)
    leeway: int = field(default_factory=lambda: _get_int("JWT", "LEEWAY", 0))


postgres_cfg = PostgresCfg()
granian_cfg = GranianCfg()
redis_cfg = RedisCfg()
docs_cfg = DocsCfg()
cors_cfg = CorsCfg()
security_cfg = SecurityCfg()
jwt_cfg = JwtCfg()
