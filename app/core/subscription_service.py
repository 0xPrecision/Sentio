from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from redis.asyncio import Redis
from datetime import datetime, timedelta, timezone
from app.providers.stars.schemas import StarsEvent
from app.infra.models import Tenant, Subscription, EventLog, Invoice

async def _resolve_tenant_id(s: AsyncSession, tenant_slug: str | None):
    if not tenant_slug:
        return None, None
    res = await s.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    t = res.scalar_one_or_none()
    return (str(t.id), t) if t else (None, None)

async def handle_subscription_event(s: AsyncSession, redis: Redis, ev: StarsEvent) -> None:
    tenant_id, tenant = await _resolve_tenant_id(s, ev.tenant_slug)

    s.add(EventLog(tenant_id=tenant_id, kind=f"stars:{ev.type}", ext_id=ev.external_id,
                   idempotency_key=f"stars:{ev.type}:{ev.external_id}", payload=ev.raw,
                   created_at=datetime.now(timezone.utc)))

    if tenant_id:
        status_map = {
            "created": ("active", False),
            "renewed": ("active", False),
            "canceled": ("canceled", True),
            "failed": ("past_due", False),
        }
        new_status, cancel_at_period_end = status_map.get(ev.type, ("active", False))

        await s.execute(
            insert(Subscription)
            .values(
                tenant_id=tenant_id,
                provider="telegram_stars",
                external_id=ev.external_id,
                status=new_status,
                period="monthly",
                next_charge_at=datetime.now(timezone.utc) + timedelta(days=30),  # TODO(api)
                cancel_at_period_end=cancel_at_period_end,
            )
            .on_conflict_do_update(
                index_elements=[Subscription.external_id],
                set_={
                    "status": new_status,
                    "cancel_at_period_end": cancel_at_period_end,
                },
            )
        )

        await s.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(plan_status=new_status)
        )

    inv_id = ev.raw.get("invoice_id") if isinstance(ev.raw, dict) else None
    if inv_id and tenant_id:
        await s.execute(
            insert(Invoice)
            .values(
                tenant_id=tenant_id,
                provider="telegram_stars",
                external_id=inv_id,
                amount=ev.raw.get("data", {}).get("amount", 0),  # TODO(api)
                currency=ev.raw.get("data", {}).get("currency", "XTR"),
                status=ev.raw.get("data", {}).get("status", "paid"),
                created_at=datetime.now(timezone.utc),
            )
            .on_conflict_do_nothing(index_elements=[Invoice.external_id])
        )

    if tenant_id and ev.type in {"failed", "canceled"}:
        from app.workers.tasks_dunning import dunning_notify
        # schedule Day0
        dunning_notify.send(tenant_id, day=0)

    await s.commit()
