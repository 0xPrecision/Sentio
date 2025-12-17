from typing import Annotated, TYPE_CHECKING

from sqlalchemy import ForeignKey, INTEGER, String, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentio.models.database import Base, ISActiveMixin, IDMixin, TenantScopedMixin, TimestampMixin

if TYPE_CHECKING:
    from sentio.models.tenant import Tenant, Location
    from sentio.models.user import User
    from sentio.models.booking import WorkSchedule, Booking, TimeSlot

string_col = Annotated[str, mapped_column(String(255), nullable=False)]


class StaffMember(Base, IDMixin, TenantScopedMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "staff_members"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    display_name: Mapped[string_col]
    bio: Mapped[str | None] = mapped_column(String(1024))
    color_hex: Mapped[str | None] = mapped_column(String(7))
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"))

    # ----- Relations -----
    tenant: Mapped["Tenant"] = relationship(back_populates="staff_members")
    location: Mapped["Location"] = relationship(back_populates="staff_members")
    user: Mapped["User"] = relationship(back_populates="staff_members")
    work_schedules: Mapped[list["WorkSchedule"]] = relationship(
        back_populates="staff_member", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="staff_member",
    )
    services: Mapped[list["Service"]] = relationship(
        secondary="staff_services", back_populates="staff_members", viewonly=True
    )
    staff_services: Mapped[list["StaffService"]] = relationship(
        back_populates="staff_member", cascade="all, delete-orphan"
    )
    time_slots: Mapped[list["TimeSlot"]] = relationship(back_populates="staff_member")


class Service(Base, IDMixin, TenantScopedMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "services"

    name: Mapped[string_col]
    duration_minutes: Mapped[int] = mapped_column(INTEGER, nullable=False)
    price_minor: Mapped[int] = mapped_column(INTEGER, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # "USD", "EUR", "BYN"
    description: Mapped[str | None] = mapped_column(String(512))
    image_url: Mapped[str | None] = mapped_column(String(512))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"))

    # ----- Relations -----
    tenant: Mapped["Tenant"] = relationship(back_populates="services")
    location: Mapped["Location"] = relationship(back_populates="services")
    staff_members: Mapped[list["StaffMember"]] = relationship(
        secondary="staff_services", back_populates="services", viewonly=True
    )
    staff_services: Mapped[list["StaffService"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="service")


class StaffService(Base, IDMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "staff_services"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "staff_member_id", "service_id", name="uq_staff_service_per_tenant"
        ),
    )
    staff_member_id: Mapped[int] = mapped_column(
        ForeignKey("staff_members.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    custom_price_minor: Mapped[int | None] = mapped_column(INTEGER)
    custom_duration_minutes: Mapped[int | None] = mapped_column(INTEGER)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ----- Relations -----
    staff_member: Mapped["StaffMember"] = relationship(back_populates="staff_services")
    service: Mapped["Service"] = relationship(back_populates="staff_services")
