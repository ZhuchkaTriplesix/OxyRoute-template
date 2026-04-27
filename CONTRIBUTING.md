# Contributing

Thanks for taking the time to contribute. This template targets **Python 3.14+** and **OxyRoute 0.3.0**.

## Local setup

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -U pip uv
uv pip install -r requirements.txt
cp config.ini.example config.ini
cp alembic.ini.example alembic.ini
```

## Running tests

```bash
make test
```

The default test suite contains smoke tests that do not require Postgres or Redis. Tests marked `@pytest.mark.integration` need a live database / Redis.

## Linting and formatting

```bash
make lint     # ruff check
make format   # ruff check --fix && ruff format
```

## Creating a database migration

```bash
make migrate-create
# enter a short message at the prompt
make migrate
```

## Pull requests

- Keep PRs focused; describe the user-visible change.
- Add or update tests for new behaviour.
- Run `make lint` and `make test` before pushing.
- Do not commit `config.ini`, `alembic.ini`, or anything from `docker/.env`.

## Project layout reference

See `README.md` for the directory map and the architectural notes that explain how OxyRoute concepts (RSGI lifespan, `Depends`, `apply_cors`) are wired into this template.
