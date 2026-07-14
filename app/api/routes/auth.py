from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.user import User
from app.schemas.auth import LogoutRequest, TokenResponse, UserLogin
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService
from app.services.create_user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> User:
    user = await UserService(session).create_user(payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username or email already registered",
        )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    tokens = await AuthService(session).login(payload.username, payload.password)
    if tokens is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    access_token, refresh_token = tokens
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(
    payload: LogoutRequest, session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    # TODO(auth): a real logout should identify the caller from their
    # authenticated request (access token) rather than a posted refresh token.
    revoked = await AuthService(session).logout(payload.refresh_token)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token"
        )
    return {"status": "logged out"}
