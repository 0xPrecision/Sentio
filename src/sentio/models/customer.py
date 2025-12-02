from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, Enum, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentio.models.database import Base, ISActiveMixin, IDMixin, TimestampMixin, TenantScopedMixin
from sentio.models.enums import BookingStatus

if TYPE_CHECKING:
    from sentio.models.booking import Booking
    from sentio.models.tenant import Tenant

class Customer(Base, IDMixin, TimestampMixin):
    __tablename__ = "customers"

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    avatar_url: Mapped[str | None] = mapped_column(String(512))

    # ----- Relations -----
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="customer"
    )
    tenant_customers: Mapped[list["TenantCustomer"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan"
    )
    #TODO favorite_locations через таблицы избранного


class TenantCustomer(Base, IDMixin, TenantScopedMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "tenant_customers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "customer_id", name="uq_tenant_customer_tenant_customer"),
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False
    )
    payment_method_id: Mapped[str | None] = mapped_column(String(128))
    card_last_4: Mapped[str | None] = mapped_column(String(4))
    card_brand: Mapped[str | None] = mapped_column(String(32))
    last_booking_status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="last_booking_status_enum"),
        default=BookingStatus.NO_HISTORY
    )
    late_cancellation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ----- Relations -----
    tenant: Mapped["Tenant"] = relationship(
        back_populates="tenant_customers"
    )
    customer: Mapped["Customer"] = relationship(
        back_populates="tenant_customers"
    )