from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.staff import Service
from sentio.repositories.services import ServiceRepository
from sentio.schemas.services import ServiceCreate, ServiceUpdate


class ServiceManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.services = ServiceRepository(session)

    async def create_service(self, tenant_id: int, data: ServiceCreate) -> Service:
        async with self.session.begin():
            service_data = data.model_dump()
            service = Service(
                tenant_id=tenant_id,
                **service_data,
            )
            await self.services.add(service)

        return service

    async def get_by_name_for_tenant(self, tenant_id: int, service_name: str) -> Service | None:
        return await self.services.get_by_name_for_tenant(tenant_id=tenant_id, name=service_name)

    async def get_by_id_for_tenant(self, tenant_id: int, service_id: int) -> Service | None:
        return await self.services.get_by_id_for_tenant(service_id=service_id, tenant_id=tenant_id)

    async def list_by_tenant(self, tenant_id: int) -> list[Service]:
        return await self.services.list_by_tenant_id(tenant_id)

    async def list_by_tenant_with_location(self, tenant_id: int, location_id: int) -> list[Service]:
        return await self.services.list_by_tenant_with_location(
            tenant_id=tenant_id, location_id=location_id
        )

    async def update_service(self, tenant_id: int, service_id: int, data: ServiceUpdate) -> Service:
        async with self.session.begin():
            service = await self.services.get_by_id_for_tenant(
                service_id=service_id, tenant_id=tenant_id
            )
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(service, field, value)

            return service
