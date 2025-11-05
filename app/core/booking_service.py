from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.infra.models import Slot, Appointment
from datetime import datetime

class BookingError(Exception):
    pass

class BookingService:
    def __init__(self, s: AsyncSession, tenant_id):
        self.s = s
        self.tenant_id = tenant_id

    async def book(self, client_id, staff_id, service_id, start_ts: datetime, end_ts: datetime) -> Appointment:
        q = (
            select(Slot).where(
                Slot.tenant_id == self.tenant_id,
                Slot.staff_id == staff_id,
                Slot.start_ts == start_ts,
            ).with_for_update()
        )
        row = (await self.s.execute(q)).scalar_one_or_none()
        if not row or row.status != "free":
            raise BookingError("slot_taken")
        await self.s.execute(
            update(Slot).where(Slot.id == row.id).values(status="booked")
        )
        appt = Appointment(
            tenant_id=self.tenant_id,
            client_id=client_id,
            staff_id=staff_id,
            service_id=service_id,
            start_ts=start_ts,
            end_ts=end_ts,
            status="booked",
            origin="user",
        )
        self.s.add(appt)
        await self.s.commit()
        return appt

    async def reschedule(self, appt_id, new_staff_id, new_start: datetime, new_end: datetime) -> Appointment:
        q = (
            select(Slot).where(
                Slot.tenant_id == self.tenant_id,
                Slot.staff_id == new_staff_id,
                Slot.start_ts == new_start,
            ).with_for_update()
        )
        slot = (await self.s.execute(q)).scalar_one_or_none()
        if not slot or slot.status != "free":
            raise BookingError("slot_taken")
        await self.s.execute(update(Slot).where(Slot.id == slot.id).values(status="booked"))
        await self.s.execute(
            update(Appointment)
            .where(Appointment.id == appt_id, Appointment.tenant_id == self.tenant_id)
            .values(start_ts=new_start, end_ts=new_end)
        )
        # TODO: free old slot after mapping appt->slot is defined
        await self.s.commit()
        appt = (await self.s.execute(select(Appointment).where(Appointment.id == appt_id))).scalar_one()
        return appt
