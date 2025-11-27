import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from sentio.models.database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow),
]
is_active = Annotated[bool, mapped_column(default=True)]


class Tenant(Base):
    __tablename__ = "tenant"
    id: Mapped[intpk]
    timezone: Mapped[str]  # TODO
    name: Mapped[str]
    contact_email: Mapped[str]
    phone: Mapped[int]
    plan: Mapped[str]
    settings_json: Mapped[str]  # TODO
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Location(Base):
    __tablename__ = "location"
    id: Mapped[intpk]
    tenant_id: Mapped[int]
    name: Mapped[str]
    address: Mapped[str]
    description: Mapped[str]
    rating: Mapped[int]  # TODO
    is_active: Mapped[is_active]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class User(Base):
    __tablename__ = "user"
    id: Mapped[intpk]
    telegram_id: Mapped[int]
    full_name: Mapped[str]
    phone: Mapped[int | None]
    email: Mapped[str]
    avatar_url: Mapped[str]
    is_active: Mapped[is_active]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class TenantUser(Base):
    __tablename__ = "tenant_user"
    id: Mapped[intpk]
    location_id: Mapped[int]
    tenant_id: Mapped[int]
    user_id: Mapped[int]
    role: Mapped[str]
    is_active: Mapped[is_active]


class StaffMember(Base):
    __tablename__ = "staff_member"
    id: Mapped[intpk]
    tenant_id: Mapped[int]
    user_id: Mapped[int]
    is_active: Mapped[is_active]


class Service(Base):
    __tablename__ = "service"
    id: Mapped[intpk]
    tenant_id: Mapped[int]
    duration: Mapped[int]
    price: Mapped[Decimal]
    description: Mapped[str]
    image_url: Mapped[str]
    is_active: Mapped[is_active]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[intpk]
    telegram_id: Mapped[int]
    full_name: Mapped[str]
    phone: Mapped[int | None]
    avatar_url: Mapped[str | None]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class TenantCustomer(Base):
    __tablename__ = "tenant_customer"
    id: Mapped[intpk]
    customer_id: Mapped[int]
    tenant_id: Mapped[int]
    card_number: Mapped[str | None]
    last_booking_status: Mapped[str]
    late_cancellation: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[is_active]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class WorkSchedule(Base):
    __tablename__ = "work_schedule"
    id: Mapped[intpk]
    staff_member_id: Mapped[int]
    date_range: Mapped[datetime.datetime]
    start_time: Mapped[datetime.datetime]
    end_time: Mapped[datetime.datetime]


class TimeSlot(Base):
    __tablename__ = "timeslot"
    id: Mapped[intpk]
    tenant_id: Mapped[int]
    staff_member_id: Mapped[int]
    service_id: Mapped[int]
    start_time: Mapped[datetime.datetime]
    end_time: Mapped[datetime.datetime]
    status: Mapped[str] = mapped_column(default="available")
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Booking(Base):
    __tablename__ = "booking"
    id: Mapped[intpk]
    tenant_id: Mapped[int]
    customer_id: Mapped[int]
    staff_member_id: Mapped[int]
    service_id: Mapped[int]
    timeslot_id: Mapped[int]
    status: Mapped[str]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
