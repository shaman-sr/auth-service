from fastapi import APIRouter, HTTPException, status

from app.core.db import ping_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness check — does not touch the database."""
    return {"status": "ok"}


@router.get("/health/db")
async def health_db() -> dict[str, str]:
    """Readiness check — confirms the database connection is live."""
    try:
        await ping_db()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"database": "ok"}
