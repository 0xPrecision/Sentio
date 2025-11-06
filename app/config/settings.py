from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore", case_sensitive=False)

    app_env: str = "dev"
    tz: str = "Europe/Minsk"

    bot_token: SecretStr
    bot_username: str

    database_url: SecretStr
    redis_url: str

    stars_provider_token: SecretStr
    stars_webhook_secret: SecretStr

    api_secret: SecretStr

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

settings = Settings()
