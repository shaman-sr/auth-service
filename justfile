setup:  uv sync
dev:    uv run uvicorn app.main:app --reload
test:   uv run pytest -q
lint:   uv run ruff format --check . && uv run ruff check . && uv run mypy app
build:  docker build -t auth-service .
up:     docker compose up --build
down:   docker compose down -v
