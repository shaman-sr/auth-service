from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

import app.models  # noqa: F401 - register tables on metadata
from app.core.db import get_session
from app.main import app


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    """In-memory async SQLite session — no Docker/Postgres needed for tests."""
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as db_session:
        yield db_session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """HTTP client with get_session overridden to use the test session."""

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
