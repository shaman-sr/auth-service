import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, health
from app.core.config import settings
from app.core.db import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router)
app.include_router(auth.router)
