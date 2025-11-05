from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.infra.db import get_session
from app.infra.models import Service
from app.api.deps import get_tenant_id, plan_guard

router = APIRouter(prefix="/admin/services", tags=["admin"], dependencies=[Depends(plan_guard)])

@router.get("")
async def list_services(tenant_id: str = Depends(get_tenant_id), s: AsyncSession = Depends(get_session)):
    res = await s.execute(select(Service).where(Service.tenant_id == tenant_id))
    return [
        {"id": str(x.id), "name": x.name, "duration_min": x.duration_min, "price_stars": x.price_stars}
        for x in res.scalars().all()
    ]

@router.post("")
async def create_service(payload: dict, tenant_id: str = Depends(get_tenant_id), s: AsyncSession = Depends(get_session)):
    q = insert(Service).values(tenant_id=tenant_id, **payload).returning(Service.id)
    row = (await s.execute(q)).first()
    await s.commit()
    return {"id": str(row[0])}

@router.put("/{service_id}")
async def update_service(service_id: str, payload: dict, tenant_id: str = Depends(get_tenant_id), s: AsyncSession = Depends(get_session)):
    await s.execute(update(Service).where(Service.id == service_id, Service.tenant_id == tenant_id).values(**payload))
    await s.commit()
    return {"ok": True}

@router.delete("/{service_id}")
async def delete_service(service_id: str, tenant_id: str = Depends(get_tenant_id), s: AsyncSession = Depends(get_session)):
    await s.execute(delete(Service).where(Service.id == service_id, Service.tenant_id == tenant_id))
    await s.commit()
    return {"ok": True}
