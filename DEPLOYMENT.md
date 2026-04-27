# Deployment

This document describes the production deployment options bundled with the template.

## 1. Docker Compose (recommended)

The `docker/docker-compose.yml` file describes a three-service stack:

- `oxyroute-app` — the OxyRoute application (built from `docker/Dockerfile`).
- `postgres` — PostgreSQL with a named volume.
- `redis` — Redis with a password (from `config.ini`).

Required preparation before `docker compose up`:

1. `cp config.ini.example config.ini`
2. Set `[POSTGRES] IP = postgres` and `[REDIS] HOST = redis` so the application reaches the Compose services by name.
3. Set a strong, **non-empty** `[REDIS] PASSWORD` (Compose enables `requirepass`).
4. Set `[DOCS] PASSWORD` and (optionally) `[JWT] SECRET`.

Then either:

```bash
make up
# or
./start.sh -d
```

`start.sh` runs `docker/sync_compose_from_config.sh`, which writes `docker/.env` from `config.ini`. Compose reads that file for `POSTGRES_*`, `REDIS_*`, and `APP_PORT`.

## 2. Bare metal (systemd)

To run the app as a systemd unit, create `/etc/systemd/system/oxyroute-app.service`:

```ini
[Unit]
Description=OxyRoute Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/apps/oxyroute-template
Environment="PATH=/opt/apps/oxyroute-template/.venv/bin"
ExecStart=/opt/apps/oxyroute-template/.venv/bin/granian --interface rsgi --host 0.0.0.0 --port 8000 --workers 2 src.main:app
Restart=always
RestartSec=10

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/apps/oxyroute-template/logs

StandardOutput=append:/opt/apps/oxyroute-template/logs/app.log
StandardError=append:/opt/apps/oxyroute-template/logs/error.log
SyslogIdentifier=oxyroute-app

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oxyroute-app
sudo systemctl start oxyroute-app
```

## 3. CI/CD (GitHub Actions)

`.github/workflows/develop.yaml` ships a deploy-on-PR pipeline:

1. On a pull request to `main`, the workflow writes `config.ini` and `alembic.ini` from GitHub Secrets.
2. The repository tree is copied to the production server with `scp`.
3. `./start.sh -d` runs on the server, which syncs `docker/.env` from `config.ini` and runs `docker compose up --build -d`.

### Required GitHub Secrets

| Secret                | Purpose                                                     |
| --------------------- | ----------------------------------------------------------- |
| `PROD_SSH_PRIVATE_KEY`| SSH private key for the deployment user                     |
| `PROD_SSH_HOST`       | Hostname or IP                                              |
| `PROD_SSH_USER`       | SSH user (must own `REMOTE_PATH`)                           |
| `PROD_CONFIG_INI`     | Full content of `config.ini` (use `\n` for line breaks)     |
| `PROD_ALEMBIC_INI`    | Full content of `alembic.ini`                               |

Edit `env.REMOTE_PATH` in the workflow to match your server (default: `/opt/apps/oxyroute-template`).

## 4. Reverse proxy

`docker/nginx/nginx.conf` contains an example Nginx config (rate limiting, proxy buffering, optional WebSocket pass-through). It is **not** wired into `docker-compose.yml` by default; use it as a reference if you front the app with an Nginx container.

## 5. Operational checklist

- Set `[DOCS] ENABLED = false` in production unless you intentionally expose `/openapi.json` and `/api/docs` to the public.
- Keep `OXYROUTE_DEBUG` unset or `0` in production.
- Set `OXYROUTE_MAX_BODY_BYTES` to a sane limit; enforce a matching limit at the edge (Nginx / cloud LB).
- Use explicit `[CORS]` origins (avoid `*` if `ALLOW_CREDENTIALS = true`).
- Rotate `[DOCS] PASSWORD` and `[JWT] SECRET` regularly.
- Monitor logs via `docker compose logs -f` or systemd journal.
