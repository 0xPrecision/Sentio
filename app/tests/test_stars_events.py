import pytest
from app.providers.stars.schemas import StarsEvent
from app.core.subscription_service import handle_subscription_event
from redis.asyncio import Redis
from app.infra.db import SessionLocal

@pytest.mark.asyncio
async def test_idempotent_insert_star_event():
    async with SessionLocal() as s:
        redis = Redis.from_url("redis://localhost:6379/0")
        ev = StarsEvent(provider="telegram_stars", external_id="test123", type="created", tenant_slug=None, raw={})
        await handle_subscription_event(s, redis, ev)
        await handle_subscription_event(s, redis, ev)
