from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    REDIS_URL: str
    APP_ENV: str

    # @property
    # def DATABASE_URL_asyncpg(self):
    #     return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
