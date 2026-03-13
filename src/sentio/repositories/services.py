from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.staff import Service
from sentio.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Service)

    async def get_by_name_for_tenant(self, *, name: str, tenant_id: int) -> Service | None:
        stmt = select(Service).where(Service.tenant_id == tenant_id, Service.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_tenant(self, *, service_id: int, tenant_id: int) -> Service | None:
        stmt = select(Service).where(Service.tenant_id == tenant_id, Service.id == service_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant_id(self, tenant_id: int) -> list[Service]:
        stmt = select(Service).where(Service.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_tenant_with_location(self, tenant_id: int, location_id: int) -> list[Service]:
        stmt = select(Service).where(
            Service.tenant_id == tenant_id, Service.location_id == location_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
