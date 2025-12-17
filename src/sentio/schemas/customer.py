from pydantic import BaseModel


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    telegram_id: int | None = None
    phone: str | None = None
    avatar_url: str | None = None


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None


class TenantCustomerCreate(BaseModel):
    customer_id: int
    tenant_id: int
    payment_method_id: int | None = None
    card_last_4: str | None = None
    card_brand: str | None = None


class TenantCustomerUpdatePayment(BaseModel):
    payment_method_id: int
    card_last_4: str
    card_brand: str
