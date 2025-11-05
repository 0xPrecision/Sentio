from __future__ import annotations
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db import get_session
from app.infra.models import Tenant
from sqlalchemy import select
import hmac, hashlib
from app.config.settings import settings

async def get_tenant_id(request: Request, s: AsyncSession = Depends(get_session)) -> str:
    slug = request.query_params.get("tenant") or request.headers.get("X-Tenant")
    if not slug:
        raise HTTPException(400, "tenant required")
    res = await s.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = res.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, "tenant not found")
    return str(tenant.id)

def verify_telegram_login(params: dict[str, str]) -> bool:
    # https://core.telegram.org/widgets/login#checking-authorization
    bot_token = settings.bot_token.get_secret_value()
    data_check_string = "\n".join(sorted([f"{k}={v}" for k, v in params.items() if k != "hash"]))
    secret = hashlib.sha256(bot_token.encode()).digest()
    h = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == params.get("hash")

async def plan_guard(request: Request, s: AsyncSession = Depends(get_session)) -> None:
    slug = request.query_params.get("tenant")
    if not slug:
        raise HTTPException(400, "tenant required")
    res = await s.execute(select(Tenant).where(Tenant.slug == slug))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(404, "tenant not found")
    if t.plan_status in ("past_due", "canceled") and request.method in ("POST", "PUT", "PATCH", "DELETE"):
        raise HTTPException(402, "subscription past_due: writes disabled")
