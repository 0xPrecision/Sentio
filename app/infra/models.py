from __future__ import annotations
from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
import uuid
from datetime import datetime
from .db import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    locale: Mapped[str]
    timezone: Mapped[str]
    plan: Mapped[str]
    plan_status: Mapped[str] = mapped_column(default="trial")
    next_renewal: Mapped[datetime | None]
    trial_until: Mapped[datetime | None]
    stars_subscription_id: Mapped[str | None]
    brand: Mapped[str | None]
    logo_url: Mapped[str | None]

class Staff(Base):
    __tablename__ = "staff"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role: Mapped[str]
    name: Mapped[str]
    __table_args__ = (UniqueConstraint("tenant_id", "tg_user_id", name="uq_staff_user_per_tenant"),)

class Service(Base):
    __tablename__ = "services"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    name: Mapped[str]
    duration_min: Mapped[int]
    price_stars: Mapped[int]
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_service_name"),)

class ScheduleRule(Base):
    __tablename__ = "schedule_rules"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id", ondelete="CASCADE"))
    weekday: Mapped[int]
    start_min: Mapped[int]
    end_min: Mapped[int]
    buffer_min: Mapped[int] = mapped_column(default=0)

class ExceptionDay(Base):
    __tablename__ = "exceptions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[uuid.UUID | None]
    date: Mapped[datetime]
    kind: Mapped[str]
    window_start_min: Mapped[int | None]
    window_end_min: Mapped[int | None]

class Slot(Base):
    __tablename__ = "slots"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[uuid.UUID]
    service_id: Mapped[uuid.UUID]
    start_ts: Mapped[datetime]
    end_ts: Mapped[datetime]
    status: Mapped[str] = mapped_column(default="free")
    hold_key: Mapped[str | None]
    __table_args__ = (
        UniqueConstraint("tenant_id", "staff_id", "start_ts", name="uq_slot_unique"),
        Index("ix_slots_lookup", "tenant_id", "staff_id", "start_ts"),
    )

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    phone: Mapped[str | None]
    name: Mapped[str | None]
    tags: Mapped[list[str] | None] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint("tenant_id", "tg_user_id", name="uq_client_per_tenant"),)

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    client_id: Mapped[uuid.UUID]
    staff_id: Mapped[uuid.UUID]
    service_id: Mapped[uuid.UUID]
    start_ts: Mapped[datetime]
    end_ts: Mapped[datetime]
    status: Mapped[str]
    origin: Mapped[str]
    __table_args__ = (Index("ix_appt_lookup", "tenant_id", "start_ts"),)

class Template(Base):
    __tablename__ = "templates"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    key: Mapped[str]
    locale: Mapped[str]
    content: Mapped[str]
    __table_args__ = (UniqueConstraint("tenant_id", "key", "locale", name="uq_template"),)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID]
    provider: Mapped[str]
    external_id: Mapped[str]
    status: Mapped[str]
    period: Mapped[str]
    next_charge_at: Mapped[datetime | None]
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False)

class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID]
    provider: Mapped[str]
    external_id: Mapped[str]
    amount: Mapped[int]
    currency: Mapped[str]
    status: Mapped[str]
    created_at: Mapped[datetime]

class EventLog(Base):
    __tablename__ = "events"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None]
    kind: Mapped[str]
    ext_id: Mapped[str | None]
    idempotency_key: Mapped[str | None]
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime]
    __table_args__ = (Index("ix_events_kind_ts", "kind", "created_at"),)
