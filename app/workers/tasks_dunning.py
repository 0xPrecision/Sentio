from __future__ import annotations
import dramatiq
import asyncio
from sqlalchemy import update
from app.infra.db import SessionLocal
from app.infra.models import Tenant

@dramatiq.actor(max_retries=5, min_backoff=30_000)
def dunning_notify(tenant_id: str, day: int):
    async def _do():
        if day in (0, 3, 7):
            # TODO: send bot message
            return
        if day == 10:
            async with SessionLocal() as s:
                await s.execute(update(Tenant).where(Tenant.id == tenant_id).values(plan_status="past_due"))
                await s.commit()
    asyncio.run(_do())
