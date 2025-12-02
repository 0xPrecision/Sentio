from datetime import date, datetime, time
from typing import Annotated, TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Date, DateTime, UniqueConstraint, Index, CheckConstraint, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentio.models.database import Base, IDMixin, TimestampMixin, TenantScopedMixin
from sentio.models.enums import TimeSlotStatus, BookingStatus

if TYPE_CHECKING:
    from sentio.models.customer import Customer
    from sentio.models.staff import StaffMember, Service
    from sentio.models.tenant import Tenant


time_stamp = Annotated[datetime, mapped_column(DateTime(timezone=True), nullable=False)]


class WorkSchedule(Base, IDMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "work_schedules"

    staff_member_id: Mapped[int] = mapped_column(
        ForeignKey("staff_members.id", ondelete="CASCADE"),
        nullable=False
    )
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_at: Mapped[time] = mapped_column(Time, nullable=False)
    end_at: Mapped[time] = mapped_column(Time, nullable=False)

    # ----- Relations -----
    time_slots: Mapped[list["TimeSlot"]] = relationship(
        back_populates="work_schedule",
        cascade="all, delete-orphan"
    )
    staff_member: Mapped["StaffMember"] = relationship(
        back_populates="work_schedules"
    )


class TimeSlot(Base, IDMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "time_slots"
    __table_args__ = (
        UniqueConstraint("tenant_id", "staff_member_id", "start_at", name="uq_slot_per_staff_start"),
        Index("ix_time_slots_tenant_start", "tenant_id", "start_at"),
        CheckConstraint("end_at > start_at", name="ck_time_slots_positive_duration")
    )

    staff_member_id: Mapped[int] = mapped_column(
        ForeignKey("staff_members.id", ondelete="CASCADE"),
        nullable=False
    )
    # service_id: Mapped[int] = mapped_column(
    #     ForeignKey("services.id", ondelete="CASCADE"),
    #     nullable=False
    # )
    work_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("work_schedules.id", ondelete="CASCADE"),
        nullable=False
    )
    start_at: Mapped[time_stamp]
    end_at: Mapped[time_stamp]
    status: Mapped[TimeSlotStatus] = mapped_column(
        Enum(TimeSlotStatus, name="timeslot_status_enum"),
        default=TimeSlotStatus.AVAILABLE,
        nullable=False
    )

    # ----- Relations -----
    work_schedule: Mapped["WorkSchedule"] = relationship(
        back_populates="time_slots"
    )
    staff_member: Mapped["StaffMember"] = relationship(
        back_populates="time_slots"
    )
    booking: Mapped["Booking"] | None = relationship(
        back_populates="time_slot",
        uselist=False
    )


class Booking(Base, IDMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "bookings"

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False
    )
    staff_member_id: Mapped[int] = mapped_column(
        ForeignKey("staff_members.id", ondelete="RESTRICT"),
        nullable=False
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"),
        nullable=False
    )
    timeslot_id: Mapped[int] = mapped_column(
        ForeignKey("timeslots.id", ondelete="RESTRICT"),
        nullable=False
    )
    booking_status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status_enum"),
        default=BookingStatus.NO_HISTORY,
        nullable=False
    )

    # ----- Relations -----
    tenant: Mapped["Tenant"] = relationship(
        back_populates="bookings"
    )
    customer: Mapped["Customer"] = relationship(
        back_populates="bookings"
    )
    staff_member: Mapped["StaffMember"] = relationship(
        back_populates="bookings"
    )
    service: Mapped["Service"] = relationship(
        back_populates="bookings"
    )
    time_slot: Mapped["TimeSlot"] = relationship(
        back_populates="booking"
    )