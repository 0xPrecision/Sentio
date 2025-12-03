from typing import Any, Annotated, TYPE_CHECKING

from sqlalchemy import String, Enum, Boolean, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from sentio.models.database import Base, ISActiveMixin, IDMixin, TimestampMixin, TenantScopedMixin
from sentio.core.enums import TenantsPlan

if TYPE_CHECKING:
    from sentio.models.user import TenantUser
    from sentio.models.customer import TenantCustomer
    from sentio.models.staff import StaffMember, Service
    from sentio.models.booking import Booking

string_col = Annotated[str, mapped_column(String(255), nullable=False)]


class Tenant(Base, IDMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[string_col]
    contact_email: Mapped[string_col]
    phone: Mapped[str | None] = mapped_column(String(32))
    plan: Mapped[TenantsPlan] = mapped_column(
        Enum(TenantsPlan, name="tenants_plan_enum"),
        server_default=TenantsPlan.LITE,
        nullable=False
    )
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="UTC")
    settings_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb")
    )

    # ----- Relations -----
    locations: Mapped[list["Location"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    tenant_users: Mapped[list["TenantUser"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    tenant_customers: Mapped[list["TenantCustomer"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    staff_members: Mapped[list["StaffMember"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    services: Mapped[list["Service"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )


class Location(Base, IDMixin, TenantScopedMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "locations"

    name: Mapped[string_col]
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ----- Relations -----
    tenant: Mapped["Tenant"] = relationship(back_populates="locations")
    staff_members: Mapped[list["StaffMember"]] = relationship(
        back_populates="location",
    )
    tenant_users: Mapped[list["TenantUser"]] = relationship(
        back_populates="location",
    )
    services: Mapped[list["Service"]] = relationship(
        back_populates="location",
    )
