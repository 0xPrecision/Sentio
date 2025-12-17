from pydantic import BaseModel


class UserCreate(BaseModel):
    full_name: str
    email: str
    telegram_id: int | None = None
    phone: str | None = None
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
