# auth-service

FastAPI + SQLModel service with an async Postgres connection.

## Stack

- **uv** — env, deps, lockfile
- **FastAPI + uvicorn** — app + server
- **SQLModel** on async SQLAlchemy (`asyncpg` driver)
- **pydantic-settings** — env-based config
- **ruff / mypy / pytest** — format+lint / types / tests

## Quick start (local, no Docker)

```sh
just setup                 # uv sync
cp .env.example .env
just test                  # runs against in-memory SQLite
```

To run `just dev`, you need a Postgres reachable at `POSTGRES_HOST`
(e.g. start just the db: `docker compose up db`).

## Full stack with Docker

```sh
docker compose up --build   # or: just up
```

Then:

```sh
curl localhost:8000/health          # {"status":"ok"}
curl localhost:8000/health/db       # {"database":"ok"} — confirms live DB

# Auth flow
curl -X POST localhost:8000/auth/register -H 'content-type: application/json' \
  -d '{"username":"alice","email":"alice@example.com","password":"pw"}'
curl -X POST localhost:8000/auth/login -H 'content-type: application/json' \
  -d '{"username":"alice","password":"pw"}'          # -> access_token + refresh_token
curl -X POST localhost:8000/auth/logout -H 'content-type: application/json' \
  -d '{"refresh_token":"<refresh_token from login>"}'
```

Tear down: `docker compose down -v` (or `just down`).

## Auth flow — what's a decision left to you

The endpoints, services, and schemas are wired end to end, but the security
primitives in `app/core/security.py` are **insecure placeholders** marked with
`TODO(auth)`. Replace them to choose your real auth flow:

- `hash_password` / `verify_password` — pick a KDF (bcrypt / argon2).
- `create_access_token` / `create_refresh_token` — opaque vs JWT, claims, expiry,
  refresh rotation.
- Logout currently revokes a posted refresh token; a real logout should identify
  the caller from their authenticated request (see the `TODO(auth)` in
  `app/api/routes/auth.py`).

## Layout

```
app/
  main.py          # FastAPI app + lifespan (init_db) + routers
  api/routes/      # thin routers (health, auth)
  core/            # config, async db engine/session, security placeholders
  models/          # SQLModel tables (User)
  schemas/         # pydantic request/response models
  services/        # business logic (framework-free): UserService, AuthService
tests/             # pytest (async, in-memory SQLite)
```

Business logic belongs in `app/services`; routers stay thin.
