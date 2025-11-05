from __future__ import annotations
import dramatiq
import asyncio
from redis.asyncio import Redis
from app.config.settings import settings
from app.core.idempotency import Idempotency

@dramatiq.actor(max_retries=5, min_backoff=10_000, max_backoff=120_000)
def send_reminder(tenant_id: str, appt_id: str, phase: str):
    async def _do():
        redis = Redis.from_url(settings.redis_url)
        idem = Idempotency(redis)
        key = f"notif:{tenant_id}:{appt_id}:{phase}"
        ok = await idem.once(key, ttl_sec=3 * 24 * 3600)
        if not ok:
            return
        # TODO: fetch appointment + client and send Telegram message
        return
    asyncio.run(_do())
