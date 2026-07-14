import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: str = Field(unique=True, index=True)
    # Nullable so multiple logged-out users can coexist (unique treats NULLs
    # as distinct in Postgres). Set on login, cleared on logout.
    refresh_token: str | None = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
