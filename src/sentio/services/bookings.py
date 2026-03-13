from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.enums import BookingStatus, TimeSlotStatus
from sentio.core.exceptions import NotFoundError
from sentio.models.booking import Booking
from sentio.repositories.bookings import (
    BookingRepository,
    TimeSlotRepository,
)
from sentio.repositories.customers import TenantCustomerRepository
from sentio.repositories.services import ServiceRepository
from sentio.repositories.staff import StaffMemberRepository, StaffServiceRepository
from sentio.schemas.booking import BookingCreate, BookingReschedule
from sentio.services.exceptions import (
    BookingStatusError,
    SlotNotAvailableError,
    TimeSlotNotFoundError,
)
from sentio.services.utils import check_customer_last_booking_status, check_time_to_start


class BookingService:
    """Сервисный класс для взаимодействия с бронированием тайм-слота"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bookings = BookingRepository(session)
        self.tenant_customer = TenantCustomerRepository(session)
        self.service = ServiceRepository(session)
        self.staff_member = StaffMemberRepository(session)
        self.staff_services = StaffServiceRepository(session)
        self.time_slot = TimeSlotRepository(session)

    async def _validate_ids_for_create(self, tenant_id: int, data: BookingCreate):
        tenant_customer = await self.tenant_customer.get(data.tenant_customer_id)
        if tenant_customer is None or tenant_customer.tenant_id != tenant_id:
            raise NotFoundError("Tenant customer is not found")

        service = await self.service.get(data.service_id)
        if service is None or service.tenant_id != tenant_id:
            raise NotFoundError("Service is not found")

        staff_member = await self.staff_member.get(data.staff_member_id)
        if staff_member is None or staff_member.tenant_id != tenant_id:
            raise NotFoundError("Staff member is not found")

        relation = await self.staff_services.get_by_keys(
            tenant_id=tenant_id, staff_member_id=data.staff_member_id, service_id=data.service_id
        )
        if relation is None:
            raise NotFoundError("Service is not available for this staff member")

    async def get_by_id_for_tenant(self, tenant_id: int, booking_id: int) -> Booking:
        booking = await self.bookings.get_by_id_for_tenant(
            tenant_id=tenant_id, booking_id=booking_id
        )
        if booking is None:
            raise NotFoundError("Booking not found")
        return booking

    async def create_booking(
        self, tenant_id: int, data: BookingCreate | BookingReschedule
    ) -> Booking:
        """Создать бронирование"""
        await self._validate_ids_for_create(tenant_id, data)

        async with self.session.begin():
            slot = await self.time_slot.get_for_update(
                tenant_id=tenant_id, time_slot_id=data.time_slot_id
            )

            if slot is None or slot.tenant_id != tenant_id:
                raise NotFoundError("Time slot not found")
            elif slot.staff_member_id != data.staff_member_id:
                raise TimeSlotNotFoundError
            elif slot.status != TimeSlotStatus.AVAILABLE:
                raise SlotNotAvailableError

            slot.status = TimeSlotStatus.BOOKED

            create_data = data.model_dump()
            booking = Booking(
                tenant_id=tenant_id, **create_data, booking_status=BookingStatus.CONFIRMED
            )
            await self.bookings.add(booking)

        return booking

    async def list_by_status(self, booking_status: BookingStatus, tenant_id: int) -> list[Booking]:
        """Получить список бронирований с определённым статусом"""
        return await self.bookings.list_by_booking_status(booking_status, tenant_id)

    async def cancel_booking(
        self,
        tenant_id: int,
        booking_id: int,
    ) -> Booking:
        """Отменить бронирование"""
        booking_obj = await self.bookings.get_by_id_for_tenant(
            tenant_id=tenant_id, booking_id=booking_id
        )
        if booking_obj is None:
            raise NotFoundError("Booking not found")

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

    async def reschedule_booking_for_customer(
        self, tenant_id: int, booking_id: int, data: BookingReschedule
    ) -> Booking:
        """Перенести бронирование"""
        # TODO сделать атомарной
        booking = await self.bookings.get_by_id_for_tenant(
            tenant_id=tenant_id, booking_id=booking_id
        )

        if booking.booking_status != BookingStatus.CONFIRMED:
            raise BookingStatusError

        await self.cancel_booking(tenant_id=tenant_id, booking_id=booking_id)
        return await self.create_booking(tenant_id=tenant_id, data=data)
