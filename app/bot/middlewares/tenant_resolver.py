from __future__ import annotations
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.models import Tenant

class TenantContext:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id

class TenantResolver(BaseMiddleware):
    def __init__(self, session_factory: Callable[[], Awaitable[AsyncSession]]):
        self._session_factory = session_factory

    async def __call__(self, handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], event: Message | CallbackQuery, data: dict[str, Any]) -> Any:  # type: ignore[override]
        tenant_ctx = None
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            parts = event.text.split()
            if len(parts) > 1 and parts[1].startswith("tn-"):
                slug = parts[1][3:]
                async with self._session_factory() as s:
                    res = await s.execute(Tenant.__table__.select().where(Tenant.slug == slug))
                    row = res.first()
                    if row:
                        tenant_ctx = TenantContext(row[0].id)
        data["tenant_ctx"] = tenant_ctx
        return await handler(event, data)
