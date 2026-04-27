# Quickstart

The shortest path from clone to running app.

## Prerequisites

- Docker Engine + Docker Compose v2
- (Optional) Python 3.14 and `uv` for local development

## 5-minute path

```bash
# 1. Clone and enter the project
git clone <your-fork>.git
cd OxyRoute-template

# 2. Configure (edit values as needed)
cp config.ini.example config.ini
cp alembic.ini.example alembic.ini

# 3. Start the development stack (Postgres, Redis, app with hot-reload)
make dev
```

The app is now serving on <http://localhost:8000>:

- `GET /api/root/health`     — health check (DB + Redis)
- `GET /api/root/version`    — build version
- `GET /openapi.json`        — auto-generated OpenAPI spec
- `GET /api/docs`            — Scalar API Reference UI (HTTP Basic from `[DOCS]`)

## Run without Docker

```bash
python3.14 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# point IP/HOST in config.ini to localhost (default)
alembic upgrade head
granian --interface rsgi src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Production-like compose

```bash
# In config.ini set:
#   [POSTGRES] IP = postgres
#   [REDIS]    HOST = redis
#   [REDIS]    PASSWORD = <strong password>

make up
# or
./start.sh -d
```

## Adding a new endpoint

1. Create a router file under `src/routers/<feature>/router.py`.
2. Register it in `src/routers/__init__.py` (`Router.routers` list).
3. If you need DB access, declare the dependency:

   ```python
   from oxyroute import APIRouter, Depends
   from src.database.dependencies import get_session_factory

   router = APIRouter()

   @router.get("/items/:item_id",
       dependencies=[("session_factory", Depends(get_session_factory))])
   async def get_item(item_id: int, session_factory) -> dict:
       async with session_factory() as session, session.begin():
           ...
           return {"id": item_id}
   ```

4. Add a test under `tests/`.
