from pydantic import BaseModel

from sentio.core.enums import BookingStatus


class BookingCreate(BaseModel):
    tenant_customer_id: int
    staff_member_id: int
    service_id: int
    time_slot_id: int


class BookingRead(BaseModel):
    id: int
    tenant_customer_id: int
    staff_member_id: int
    service_id: int
    time_slot_id: int
    booking_status: BookingStatus


class BookingReschedule(BaseModel):
    staff_member_id: int
    service_id: int
    time_slot_id: int
