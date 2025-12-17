from datetime import date, datetime, time

from pydantic import BaseModel


class WorkScheduleCreate(BaseModel):
    tenant_id: int
    staff_member_id: int
    work_date: date
    start_at: time
    end_at: time


class WorkScheduleUpdate(BaseModel):
    work_date: date | None = None
    start_at: time | None = None
    end_at: time | None = None


class TimeSlotCreate(BaseModel):
    tenant_id: int
    staff_member_id: int
    work_schedule_id: int
    start_at: datetime
    end_at: datetime


class BookingCreate(BaseModel):
    tenant_id: int
    customer_id: int
    staff_member_id: int
    service_id: int
    time_slot_id: int
