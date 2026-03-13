from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sentio.core.enums import Environment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    app_env: Environment = Field(default=Environment.DEV)
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    postgres_user: str = Field(default="sentio")
    postgres_password: str = Field(default="sentio")
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    db_name: str = Field(default="sentio")

    redis_url: str = Field(default="redis://redis:6379/0")

    sqlalchemy_echo: bool = Field(default=False)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.db_name}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
