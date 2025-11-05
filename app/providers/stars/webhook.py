from __future__ import annotations
from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.config.settings import settings
from app.infra.db import get_session
from app.providers.stars.client import StarsClient
from app.providers.stars.schemas import StarsEvent, StarsWebhookPayload
from app.core.subscription_service import handle_subscription_event
from app.core.idempotency import get_idem

router = APIRouter(prefix="/stars", tags=["stars"])

async def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)

@router.post("/webhook")
async def stars_webhook(
    req: Request,
    s: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    body = await req.body()
    sig = req.headers.get("X-Stars-Signature", "")  # TODO(api): header name
    client = StarsClient(settings.stars_webhook_secret.get_secret_value())

    if not client.verify_signature(sig, body):
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = await req.json()
    ev_raw: StarsWebhookPayload = payload  # type: ignore[assignment]

    event_type_map = {
        "subscription_created": "created",
        "subscription_renewed": "renewed",
        "subscription_canceled": "canceled",
        "subscription_failed": "failed",
    }
    type_norm = event_type_map.get(ev_raw.get("event", ""), "created")
    ext_id = ev_raw.get("subscription_id") or ev_raw.get("invoice_id") or "unknown"
    tenant_slug = ev_raw.get("tenant_slug")

    event = StarsEvent(
        provider="telegram_stars",
        external_id=ext_id,
        type=type_norm,  # type: ignore[arg-type]
        tenant_slug=tenant_slug,
        raw=ev_raw,
    )

    idem = await get_idem(redis)
    key = f"stars:{event.type}:{event.external_id}"
    if not await idem.once(key, ttl_sec=7 * 24 * 3600):
        return JSONResponse({"ok": True, "duplicate": True})

    await handle_subscription_event(s, redis, event)
    return {"ok": True}
