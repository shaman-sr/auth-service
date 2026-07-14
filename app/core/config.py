from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "auth-service"

    postgres_user: str = "auth"
    postgres_password: str = "auth"
    postgres_db: str = "auth"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy URL using the asyncpg driver."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
