from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.exceptions import NotFoundError
from sentio.models.booking import WorkSchedule
from sentio.repositories.bookings import WorkScheduleRepository
from sentio.repositories.staff import StaffMemberRepository
from sentio.schemas.work_schedules import WorkScheduleCreate, WorkScheduleUpdate
from sentio.services.exceptions import DateValidationError, TimeValidationError


class WorkScheduleService:
    """Сервисный класс для изменения рабочего расписания мастера на один день"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.work_schedules = WorkScheduleRepository(session)
        self.staff_members = StaffMemberRepository(session)

    async def _validate_data(self, tenant_id: int, data: WorkScheduleCreate | WorkScheduleUpdate):
        if data.start_at and data.end_at:
            if data.start_at >= data.end_at:
                raise TimeValidationError
        if data.work_date is not None:
            if data.work_date < date.today():
                raise DateValidationError
        if data.staff_member_id is not None:
            staff_member = await self.staff_members.get(data.staff_member_id)
            if staff_member is None or staff_member.tenant_id != tenant_id:
                raise NotFoundError("Staff member not found")

    async def get_work_schedule(self, tenant_id: int, schedule_id: int) -> WorkSchedule:
        """Функция для получения рабочего расписания"""
        work_schedule = await self.work_schedules.get_by_id_for_tenant(
            tenant_id=tenant_id,
            schedule_id=schedule_id,
        )
        if work_schedule is None:
            raise NotFoundError("Work schedule not found")

        return work_schedule

    async def create_work_schedule(self, tenant_id: int, data: WorkScheduleCreate) -> WorkSchedule:
        await self._validate_data(data=data, tenant_id=tenant_id)

        async with self.session.begin():
            create_data = data.model_dump()
            work_schedule = WorkSchedule(tenant_id=tenant_id, **create_data)
            await self.work_schedules.add(work_schedule)

            return work_schedule

    async def update_work_schedule(
        self,
        schedule_id: int,
        tenant_id: int,
        data: WorkScheduleUpdate,
    ) -> WorkSchedule:
        """Функция для изменения рабочего расписания"""
        await self._validate_data(tenant_id=tenant_id, data=data)
        work_schedule = await self.work_schedules.get_by_id_for_tenant(
            schedule_id=schedule_id, tenant_id=tenant_id
        )
        if work_schedule is None:
            raise NotFoundError("Work schedule is not found")

        if data.work_date is not None:
            if data.work_date < work_schedule.work_date:
                raise DateValidationError
            elif data.work_date == work_schedule.work_date and data.start_at is not None:
                if data.start_at < work_schedule.start_at:
                    raise TimeValidationError

        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(work_schedule, field, value)

            return work_schedule
