from datetime import time

from pydantic import BaseModel

from sentio.core.enums import TimeSlotStatus


class TimeSlotCreate(BaseModel):
    staff_member_id: int
    work_schedule_id: int
    start_at: time
    end_at: time


class TimeSlotRead(BaseModel):
    staff_member_id: int
    work_schedule_id: int
    start_at: time
    end_at: time
    status: TimeSlotStatus
