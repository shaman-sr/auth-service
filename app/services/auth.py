from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import or_, select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def _get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def create_user(self, user: UserCreate) -> User | None:
        """Create a user, or return None if the username/email is taken."""
        statement = select(User).where(
            or_(User.username == user.username, User.email == user.email)
        )
        result = await self.session.execute(statement)
        if result.scalars().first() is not None:
            return None

        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password),
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user


    async def login(self, username: str, password: str) -> tuple[str, str] | None:
        """Verify credentials and issue tokens, or return None on failure.

        Persists the refresh token on the user so logout can revoke it.
        """
        user = await self._get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            return None

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        user.refresh_token = refresh_token
        user.updated_at = datetime.now()
        self.session.add(user)
        await self.session.commit()
        return access_token, refresh_token

    async def logout(self, refresh_token: str) -> bool:
        """Revoke a refresh token. Returns False if it isn't recognized."""
        result = await self.session.execute(select(User).where(User.refresh_token == refresh_token))
        user = result.scalars().first()
        if user is None:
            return False

        user.refresh_token = None
        user.updated_at = datetime.now()
        self.session.add(user)
        await self.session.commit()
        return True
