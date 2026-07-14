import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency yielding an async DB session."""
    async with async_session_maker() as session:
        yield session


async def init_db(retries: int = 10, delay: float = 1.5) -> None:
    """Wait for Postgres to accept connections, then create tables.

    The retry loop is what guarantees the app comes up even when it starts
    before Postgres is ready (e.g. in docker-compose).
    """
    # Import models so their tables are registered on SQLModel.metadata
    # before create_all runs.
    import app.models  # noqa: F401

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Database ready (tables created).")
            return
        except Exception as exc:  # noqa: BLE001 - retry on any connection error
            last_error = exc
            logger.warning("Database not ready (attempt %d/%d): %s", attempt, retries, exc)
            await asyncio.sleep(delay)

    raise RuntimeError(
        f"Could not connect to the database after {retries} attempts"
    ) from last_error


async def ping_db() -> None:
    """Execute a trivial query to confirm the DB connection is live."""
    async with async_session_maker() as session:
        await session.execute(text("SELECT 1"))
