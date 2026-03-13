from datetime import date, time

from pydantic import BaseModel


class WorkScheduleCreate(BaseModel):
    staff_member_id: int
    work_date: date
    start_at: time
    end_at: time


class WorkScheduleRead(BaseModel):
    id: int
    staff_member_id: int
    work_date: date
    start_at: time
    end_at: time


class WorkScheduleUpdate(BaseModel):
    staff_member_id: int | None = None
    work_date: date | None = None
    start_at: time | None = None
    end_at: time | None = None
