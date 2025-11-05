from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infra.db import get_session
from app.infra.models import Subscription, Tenant
from app.api.deps import get_tenant_id

router = APIRouter(prefix="/admin/subscription", tags=["admin"]) 

@router.get("")
async def view_subscription(tenant_id: str = Depends(get_tenant_id), s: AsyncSession = Depends(get_session)):
    sub = (await s.execute(select(Subscription).where(Subscription.tenant_id == tenant_id))).scalar_one_or_none()
    ten = (await s.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one()
    return {
        "plan": ten.plan,
        "plan_status": ten.plan_status,
        "subscription": {
            "provider": sub.provider if sub else None,
            "status": sub.status if sub else None,
            "next_charge_at": sub.next_charge_at.isoformat() if sub and sub.next_charge_at else None,
        },
    }

@router.post("/cancel_at_period_end")
async def cancel_at_period_end(tenant_id: str = Depends(get_tenant_id)):
    # TODO(api): Stars cancel flow (adapter method)
    return {"ok": True}
