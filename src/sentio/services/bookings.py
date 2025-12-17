from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.enums import BookingStatus, TimeSlotStatus
from sentio.models.booking import WorkSchedule, TimeSlot, Booking
from sentio.repositories.bookings import WorkScheduleRepository, TimeSlotRepository, BookingRepository
from sentio.schemas.booking import WorkScheduleCreate, WorkScheduleUpdate, TimeSlotCreate, BookingCreate
from sentio.services.exceptions import SlotNotAvailableError, DateValidationError, BookingStatusError
from sentio.services.utils import check_customer_last_booking_status, check_time_to_start


class WorkScheduleService:
    """Сервисный класс для изменения рабочего расписания мастера на один день"""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.work_schedules = WorkScheduleRepository(session)

    async def get_or_create_work_schedule(
            self,
            data: WorkScheduleCreate
    ) -> WorkSchedule:
        """Функция для получения или создания рабочего расписания"""
        if data.work_date < date.today():
            raise DateValidationError

        async with self.session.begin():
            work_schedule = await self.work_schedules.get_by_staff_and_date(
                staff_member_id=data.staff_member_id,
                tenant_id=data.tenant_id,
                work_date=data.work_date
            )
            if work_schedule is not None:
                return work_schedule

            create_data = data.model_dump()
            work_schedule = WorkSchedule(
                **create_data
            )
            await self.work_schedules.add(work_schedule)

        return work_schedule

    async def update_work_schedule(
            self,
            work_schedule: WorkSchedule,
            data: WorkScheduleUpdate,
    ) -> WorkSchedule:
        """Функция для изменения рабочего расписания"""
        if data.work_date is not None and data.work_date < date.today():
            raise DateValidationError

        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(work_schedule, field, value)

            return work_schedule


class TimeSlotService:
    """Сервисный класс для взаимодействия с тайм-слотом"""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.time_slots = TimeSlotRepository(session)

    async def get_or_create_available_slot(
            self,
            data: TimeSlotCreate
    ) -> TimeSlot:
        """Получить или создать тайм-слот"""
        async with self.session.begin():
            time_slot = await self.time_slots.get_by_work_ids_and_time(
                staff_member_id=data.staff_member_id,
                tenant_id=data.tenant_id,
                start_at=data.start_at
            )
            if time_slot is not None:
                if time_slot.status == TimeSlotStatus.AVAILABLE:
                    return time_slot
                else:
                    raise SlotNotAvailableError

            create_data = data.model_dump()
            time_slot = TimeSlot(
                **create_data,
            )
            await self.time_slots.add(time_slot)

        return time_slot

    async def list_by_status(
            self,
            status: TimeSlotStatus,
            tenant_id: int
    ) -> list[TimeSlot]:
        """Получить список тайм-слотов с определённым статусом"""
        return await self.time_slots.list_by_status(status, tenant_id)


class BookingService:
    """Сервисный класс для взаимодействия с бронированием тайм-слота"""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bookings = BookingRepository(session)
        self.time_slots = TimeSlotRepository(session)

    async def create_booking(
            self,
            data: BookingCreate
    ) -> Booking:
        """Создать бронирование"""
        async with self.session.begin():
            slot = await self.time_slots.get_for_update(
                tenant_id=data.tenant_id,
                time_slot_id=data.time_slot_id
            )
            if slot.status != TimeSlotStatus.AVAILABLE:
                raise SlotNotAvailableError

            slot.status = TimeSlotStatus.BOOKED

            create_data = data.model_dump()
            booking = Booking(
                **create_data,
                booking_status=BookingStatus.CONFIRMED
            )
            await self.bookings.add(booking)

        return booking

    async def list_by_status(
            self,
            booking_status: BookingStatus,
            tenant_id: int
    ) -> list[Booking]:
        """Получить список бронирований с определённым статусом"""
        return await self.bookings.list_by_booking_status(booking_status, tenant_id)

    async def cancel_booking(
            self,
            booking_obj: Booking,
    ) -> Booking:
        """Отменить бронирование"""
        if booking_obj.booking_status != BookingStatus.CONFIRMED:
            raise BookingStatusError

        async with self.session.begin():
            seconds_left = check_time_to_start(booking_obj)

            if seconds_left <= 0:
                booking_obj.time_slot.status = TimeSlotStatus.EXPIRED
                booking_obj.booking_status = BookingStatus.NO_SHOW
                check_customer_last_booking_status(booking_obj)

            elif seconds_left <= 7200:
                booking_obj.time_slot.status = TimeSlotStatus.AVAILABLE
                booking_obj.booking_status = BookingStatus.CANCELLED_LATE
                check_customer_last_booking_status(booking_obj)

            else:
                booking_obj.time_slot.status = TimeSlotStatus.AVAILABLE
                booking_obj.booking_status = BookingStatus.CANCELLED
                booking_obj.tenant_customer.last_booking_status = BookingStatus.CANCELLED

        return booking_obj

    async def reschedule_booking(
            self,
            booking: Booking,
            data: BookingCreate
    ) -> Booking:
        """Перенести бронирование"""
        if booking.booking_status != BookingStatus.CONFIRMED:
            raise BookingStatusError

        await self.cancel_booking(booking)
        return await self.create_booking(data)