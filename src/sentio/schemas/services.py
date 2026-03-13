from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int
    price_minor: int
    currency: str
    description: str | None = None
    image_url: str | None = None
    location_id: int | None = None


class ServiceRead(BaseModel):
    name: str
    duration_minutes: int
    price_minor: int
    currency: str
    description: str | None = None
    image_url: str | None = None
    location_id: int | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    duration_minutes: int | None = None
    price_minor: int | None = None
    currency: str | None = None
    description: str | None = None
    image_url: str | None = None
    location_id: int | None = None
    is_active: bool | None = None
