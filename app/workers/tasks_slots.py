from __future__ import annotations
import dramatiq
from datetime import datetime, timedelta, timezone
import asyncio
from sqlalchemy import select, insert
from app.infra.db import SessionLocal
from app.infra.models import ScheduleRule, Slot, Service

LOOKAHEAD_DAYS = 45

@dramatiq.actor(max_retries=3)
def materialize_slots():
    async def _do():
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=LOOKAHEAD_DAYS)
        async with SessionLocal() as s:
            rules = (await s.execute(select(ScheduleRule))).scalars().all()
            services = {sv.id: sv for sv in (await s.execute(select(Service))).scalars().all()}
            for r in rules:
                day = now
                while day <= horizon:
                    if day.weekday() == r.weekday:
                        for sv in services.values():
                            start = day.replace(hour=r.start_min // 60, minute=r.start_min % 60, second=0, microsecond=0)
                            end = day.replace(hour=r.end_min // 60, minute=r.end_min % 60, second=0, microsecond=0)
                            t = start
                            step = timedelta(minutes=sv.duration_min + r.buffer_min)
                            while t + timedelta(minutes=sv.duration_min) <= end:
                                await s.execute(
                                    insert(Slot)
                                    .values(
                                        tenant_id=r.tenant_id,
                                        staff_id=r.staff_id,
                                        service_id=sv.id,
                                        start_ts=t,
                                        end_ts=t + timedelta(minutes=sv.duration_min),
                                        status="free"
                                    )
                                    .on_conflict_do_nothing(index_elements=[Slot.tenant_id, Slot.staff_id, Slot.start_ts])
                                )
                                t += step
                    day += timedelta(days=1)
            await s.commit()
    asyncio.run(_do())
