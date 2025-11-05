import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert
from app.infra.db import SessionLocal
from app.infra.models import Slot
from app.core.booking_service import BookingService, BookingError

@pytest.mark.asyncio
async def test_double_booking_prevented():
    start = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(hours=1)
    end = start + timedelta(minutes=30)
    tenant_id = "00000000-0000-0000-0000-000000000001"
    staff_id = tenant_id
    service_id = tenant_id
    client1 = tenant_id
    client2 = tenant_id

    async with SessionLocal() as s:
        await s.execute(insert(Slot).values(tenant_id=tenant_id, staff_id=staff_id, service_id=service_id, start_ts=start, end_ts=end, status="free"))
        await s.commit()

    async with SessionLocal() as s:
        svc1 = BookingService(s, tenant_id)
        svc2 = BookingService(s, tenant_id)

        async def try_book(svc, client):
            return await svc.book(client, staff_id, service_id, start, end)

        tasks = {asyncio.create_task(try_book(svc1, client1)), asyncio.create_task(try_book(svc2, client2))}
        done, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        results = []
        for t in done:
            try:
                results.append((True, await t))
            except BookingError:
                results.append((False, None))
        assert sum(1 for ok, _ in results if ok) == 1
        assert sum(1 for ok, _ in results if not ok) == 1
