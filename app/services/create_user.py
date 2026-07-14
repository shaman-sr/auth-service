from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import or_, select

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

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
