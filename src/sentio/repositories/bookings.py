from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.enums import TimeSlotStatus, BookingStatus
from sentio.services.exceptions import TimeSlotNotFoundError
from sentio.models.booking import WorkSchedule, TimeSlot, Booking
from sentio.repositories.base import BaseRepository


class WorkScheduleRepository(BaseRepository[WorkSchedule]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WorkSchedule)

    async def get_by_staff_and_date(
            self,
            *,
            staff_member_id: int,
            tenant_id: int,
            work_date: date
    ) -> WorkSchedule | None:
        stmt = select(WorkSchedule).where(
            WorkSchedule.staff_member_id == staff_member_id,
            WorkSchedule.tenant_id == tenant_id,
            WorkSchedule.work_date == work_date
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TimeSlotRepository(BaseRepository[TimeSlot]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TimeSlot)

    async def get_for_update(
            self,
            *,
            tenant_id: int,
            time_slot_id: int
    ) -> TimeSlot:
        stmt = (
            select(TimeSlot)
            .where(
            TimeSlot.tenant_id == tenant_id,
            TimeSlot.id == time_slot_id,)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        slot = result.scalar_one_or_none()
        if slot is None:
            raise TimeSlotNotFoundError(tenant_id=tenant_id, time_slot_id=time_slot_id)
        return slot

    async def get_by_work_ids_and_time(
            self,
            *,
            staff_member_id: int,
            tenant_id: int,
            start_at: datetime
    ) -> TimeSlot | None:
        stmt = select(TimeSlot).where(
            TimeSlot.staff_member_id == staff_member_id,
            TimeSlot.tenant_id == tenant_id,
            TimeSlot.start_at == start_at
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_status(self, status: TimeSlotStatus, tenant_id: int) -> list[TimeSlot]:
        stmt = select(TimeSlot).where(
            TimeSlot.status == status,
            TimeSlot.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Booking)

    async def get_by_work_ids(
            self,
            *,
            customer_id: int,
            staff_member_id: int,
            service_id: int,
            time_slot_id: int,
            tenant_id: int
    ) -> Booking | None:
        stmt = select(Booking).where(
            Booking.customer_id == customer_id,
            Booking.staff_member_id == staff_member_id,
            Booking.service_id == service_id,
            Booking.time_slot_id == time_slot_id,
            Booking.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_booking_status(
            self,
            booking_status: BookingStatus,
            tenant_id: int
    ) -> list[Booking]:
        stmt = select(Booking).where(
            Booking.booking_status == booking_status,
            Booking.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())