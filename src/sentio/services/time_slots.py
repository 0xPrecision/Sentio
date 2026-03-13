from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.enums import TimeSlotStatus
from sentio.core.exceptions import NotFoundError, ConflictError
from sentio.models.booking import TimeSlot
from sentio.repositories.bookings import TimeSlotRepository, WorkScheduleRepository
from sentio.repositories.staff import StaffMemberRepository
from sentio.schemas.time_slots import TimeSlotCreate
from sentio.services.exceptions import (
    SlotNotAvailableError,
    TimeSlotNotFoundError,
    TimeValidationError,
)


class TimeSlotService:
    """Сервисный класс для взаимодействия с тайм-слотом"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.time_slots = TimeSlotRepository(session)
        self.staff_members = StaffMemberRepository(session)
        self.work_schedules = WorkScheduleRepository(session)

    async def _validate_data(self, tenant_id: int, data: TimeSlotCreate):
        if data.start_at >= data.end_at:
            raise TimeValidationError

        staff_member = await self.staff_members.get(data.staff_member_id)
        if staff_member is None or staff_member.tenant_id != tenant_id:
            raise NotFoundError("Staff member not found")
        if not staff_member.is_active:
            raise ConflictError("Staff member is inactive")

        schedule = await self.work_schedules.get(data.work_schedule_id)
        if (
            schedule is None
            or schedule.tenant_id != tenant_id
            or schedule.staff_member_id != data.staff_member_id
        ):
            raise NotFoundError("Work schedule not found")

        if schedule.start_at > data.start_at or schedule.end_at < data.end_at:
            raise TimeValidationError

    async def get_available_slot(self, tenant_id: int, time_slot_id: int) -> TimeSlot:
        """Получить тайм-слот"""
        time_slot = await self.time_slots.get_by_id_for_tenant(
            tenant_id=tenant_id, time_slot_id=time_slot_id
        )

        if time_slot is None:
            raise TimeSlotNotFoundError
        elif time_slot.status == TimeSlotStatus.AVAILABLE:
            return time_slot
        else:
            raise SlotNotAvailableError

    async def create_slot(self, tenant_id: int, data: TimeSlotCreate) -> TimeSlot:
        """Создать тайм-слот"""
        await self._validate_data(tenant_id=tenant_id, data=data)

        async with self.session.begin():
            create_data = data.model_dump()
            time_slot = TimeSlot(
                tenant_id=tenant_id,
                **create_data,
            )
            await self.time_slots.add(time_slot)

        return time_slot

    async def list_by_status(self, status: TimeSlotStatus, tenant_id: int) -> list[TimeSlot]:
        """Получить список тайм-слотов с определённым статусом"""
        return await self.time_slots.list_by_status(status, tenant_id)
