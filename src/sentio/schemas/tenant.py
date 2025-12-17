from typing import Any

from pydantic import BaseModel, EmailStr, Field

from sentio.core.enums import TenantsPlan, TenantUserRole


class TenantBase(BaseModel):
    name: str
    contact_email: EmailStr
    phone: str | None = None
    plan: TenantsPlan
    slug: str
    settings: dict[str, Any] = Field(default_factory=dict)


class TenantCreateWithLocation(TenantBase):
    """Создание тенанта с дефолтной локацией"""

    default_location_name: str
    address: str
    description: str | None = None


class TenantUpdate(BaseModel):
    """Класс для обновления полей тенанта"""

    name: str | None = None
    contact_email: EmailStr | None = None
    phone: str | None = None
    plan: TenantsPlan | None = None
    slug: str | None = None
    settings: dict[str, Any] | None = None
    is_active: bool | None = None


class LocationCreate(BaseModel):
    name: str
    address: str
    description: str | None = None
    is_default: bool = False


class LocationUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    description: str | None = None
    is_default: bool | None = None


class TenantUserCreate(BaseModel):
    user_id: int
    role: TenantUserRole
    location_id: int | None = None


class TenantUserUpdate(BaseModel):
    role: TenantUserRole | None = None
    location_id: int | None = None
