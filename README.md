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
curl -X POST localhost:8000/auth/refresh -H 'content-type: application/json' \
  -d '{"refresh_token":"<refresh_token>"}'           # -> rotated token pair
curl -X POST localhost:8000/auth/logout \
  -H 'Authorization: Bearer <access_token>'          # revokes the refresh token
```

Tear down: `docker compose down -v` (or `just down`).

## Auth flow

- **Passwords** are hashed with bcrypt (`app/core/security.py`).
- **Access / refresh tokens** are signed JWTs (HS256) with `sub`, `type`, `iat`,
  `exp`, and a unique `jti`. Lifetimes and the signing key are configured in
  `app/core/config.py` (`JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
  `REFRESH_TOKEN_EXPIRE_DAYS`).
- The current refresh token is stored on the user row, so **logout** revokes it
  and **refresh rotates** it — a reused (pre-rotation or post-logout) refresh
  token is rejected.
- **Protected routes** depend on `get_current_user` (`app/api/deps.py`), which
  validates a `Bearer` access token.

⚠️ Set a strong `JWT_SECRET_KEY` in every real environment:
`python -c "import secrets; print(secrets.token_urlsafe(32))"`.

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
