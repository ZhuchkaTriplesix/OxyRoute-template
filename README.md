# OxyRoute Template

A production-ready boilerplate for building services on top of [OxyRoute](https://github.com/QueryaHub/OxyRoute) — a blazing-fast Python web framework whose hot path runs in Rust and serves [RSGI](https://github.com/emmett-framework/granian/blob/master/docs/spec/RSGI.md) under [Granian](https://github.com/emmett-framework/granian).

This template is the OxyRoute counterpart of [Reei-dp/fastapi-template](https://github.com/Reei-dp/fastapi-template), with the same project layout, Docker / CI workflow, and INI-based configuration.

## Features

- **OxyRoute 0.4.0** (RSGI) running on **Granian** with Python **3.14**.
- **Rust Hot Path DB Pool** (`setup_database` / `close_database`) & dynamic zero-copy queries via `DBQuery`.
- **Request / Response Middleware Stack** (`app.set_middleware`) demonstrated with request logging.
- **PostgreSQL** via async SQLAlchemy 2.0 + asyncpg (for full ORM and migration support).
- **Redis** for caching with a small `RedisController` helper.
- **Alembic** for database migrations.
- **Scalar API Reference** at `/api/docs` (HTTP Basic from `config.ini`); built-in `/openapi.json`.
- **CORS**, **security headers**, and a **JWT-protected route** example.
- **Docker / Docker Compose** for both development (hot-reload) and production.
- **GitHub Actions** deploy via SSH (`scp` + `start.sh -d`).
- **Makefile** for common tasks.
- **Ruff** for linting and formatting.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.14+ for local development
- `uv` (optional, used by `make install` and the Dockerfiles)
- `make` (optional)

### 1. Clone & configure

```bash
git clone <your-fork>.git
cd OxyRoute-template
cp config.ini.example config.ini
cp alembic.ini.example alembic.ini
```

Edit `config.ini` to set your Postgres / Redis credentials and `[DOCS]` / `[JWT]` secrets.

### 2. Run (development)

```bash
make dev
# or
docker compose -f docker/docker-compose.dev.yml up --build
```

The application is available at:

- App: <http://localhost:8000>
- OpenAPI JSON: <http://localhost:8000/openapi.json>
- Docs UI (Scalar): <http://localhost:8000/api/docs> (HTTP Basic from `[DOCS]`)
- Health: <http://localhost:8000/api/root/health>
- Fast DB Ping (Rust hot path): <http://localhost:8000/api/root/fast-ping>

### 3. Run (locally without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
granian --interface rsgi src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run (production-ish, with compose)

When `config.ini` has a non-empty Redis password and `[POSTGRES] IP = postgres`, `[REDIS] HOST = redis` (so the app reaches the Compose services):

```bash
make up
# or
./start.sh -d
```

This runs `docker/sync_compose_from_config.sh` (writes `docker/.env` from `config.ini`) and then `docker compose up --build` from `docker/`.

## Project Structure

```
OxyRoute-template/
|-- .github/workflows/develop.yaml   # CI/CD pipeline
|-- src/
|   |-- main.py                      # exports `app` for Granian RSGI
|   |-- config.py                    # INI loader with env-overrides
|   |-- schemas.py                   # shared Pydantic schemas
|   |-- configuration/
|   |   `-- app.py                   # OxyApp(App) with __rsgi_init__/__rsgi_del__
|   |-- routers/
|   |   |-- __init__.py              # router registry
|   |   |-- root/                    # /api/root: health, version, items
|   |   |-- docs/                    # /api/docs Scalar UI (Basic Auth)
|   |   `-- secure/                  # /api/secure: JWT example
|   |-- database/
|   |   |-- core.py                  # engine + async_sessionmaker
|   |   |-- base.py                  # DeclarativeBase
|   |   |-- dependencies.py          # get_session_factory dep
|   |   `-- alembic/                 # migrations
|   |-- redis_client/redis.py        # init + RedisController
|   `-- misc/                        # security helpers, timezone util
|-- docker/
|   |-- Dockerfile                   # production image
|   |-- Dockerfile.dev               # development image (hot-reload)
|   |-- docker-compose.yml           # app + postgres + redis
|   |-- docker-compose.dev.yml       # dev stack
|   |-- entrypoint.sh                # alembic upgrade + granian rsgi
|   |-- sync_compose_from_config.sh  # config.ini -> docker/.env
|   `-- nginx/nginx.conf             # optional reverse proxy
|-- tests/                           # smoke tests
|-- config.ini.example
|-- alembic.ini.example
|-- requirements.txt
|-- Makefile
|-- ruff.toml
|-- pyproject.toml
|-- start.sh
`-- README.md
```

## Architecture notes (vs the FastAPI template)

OxyRoute is RSGI-only and intentionally minimal — it does **not** ship an ASGI middleware stack or a `request.state` object. The template adapts the FastAPI patterns as follows:

| Concept                  | FastAPI template                              | OxyRoute template                                                     |
| ------------------------ | --------------------------------------------- | --------------------------------------------------------------------- |
| Per-process resources    | Module-level engine / sessionmaker / Redis    | `OxyApp.__rsgi_init__` writes them to `app.state`                     |
| DB session per request   | HTTP middleware on `request.state.db`         | `Depends(get_session_factory)` + `async with session.begin()`         |
| Swagger UI               | Custom `/api/docs` route with HTTP Basic      | Scalar API Reference HTML at `/api/docs` with HTTP Basic              |
| Run command              | `python -m src.main` (Granian via `__main__`) | `granian --interface rsgi src.main:app`                               |
| CORS / Security headers  | `CORSMiddleware` from FastAPI                 | `apply_cors(app, CORSConfig(...))` and `app.set_security_headers(...)` |
| JWT                      | Library, validated in dependency              | Native `require_jwt=True` + `jwt_secret=...` on the route             |

`async with session.begin()` inside the handler is the functional equivalent of the auto-commit / rollback FastAPI middleware in the original template.

## Make targets

```text
make help           # Show all targets
make install        # Install dependencies (uv pip install)
make dev            # Start dev environment (hot-reload)
make build          # Build production Docker image
make up             # Start production stack (./start.sh -d)
make down           # Stop all containers
make logs           # Tail production logs
make clean          # Remove containers and volumes
make test           # Run pytest
make lint           # ruff check
make format         # ruff check --fix && ruff format
make migrate        # alembic upgrade head
make migrate-create # alembic revision --autogenerate
make shell          # Python REPL with `app` loaded
make db-shell       # psql in dev stack
make redis-cli      # redis-cli in dev stack
```

## CI/CD

`.github/workflows/develop.yaml` runs on pull requests to `main`:

1. Writes `config.ini` and `alembic.ini` from GitHub Secrets.
2. Copies the repository tree to the server via `scp`.
3. Runs `./start.sh -d` on the server.

Required secrets:

- `PROD_SSH_PRIVATE_KEY`, `PROD_SSH_HOST`, `PROD_SSH_USER`
- `PROD_CONFIG_INI`, `PROD_ALEMBIC_INI`

Edit `env.REMOTE_PATH` in the workflow to match your deployment directory (default: `/opt/apps/oxyroute-template`).

## License

MIT.
