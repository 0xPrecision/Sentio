from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.staff import StaffMember, Service, StaffService
from sentio.repositories.staff import StaffMemberRepository, ServiceRepository, StaffServiceRepository
from sentio.schemas.staff import StaffMemberCreate, StaffMemberUpdate, ServiceCreate, ServiceUpdate


class StaffMemberService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.staff_members = StaffMemberRepository(session)

    async def get_or_create_staff_member(
            self,
            tenant_id: int,
            data: StaffMemberCreate
    ) -> StaffMember:
        async with self.session.begin():
            staff_member = await self.staff_members.get_by_name_for_tenant(
                tenant_id=tenant_id,
                name=data.display_name
            )
            if staff_member is not None:
                return staff_member

            staff_member_data = data.model_dump()

            staff_member = StaffMember(
                tenant_id=tenant_id,
                **staff_member_data,
            )
            await self.staff_members.add(staff_member)

        return staff_member

    async def get_by_name_for_tenant(self, tenant_id: int, display_name: str) -> StaffMember | None:
        return await self.staff_members.get_by_name_for_tenant(
                tenant_id=tenant_id,
                name=display_name
            )

    async def list_by_tenant(self, tenant_id: int) -> list[StaffMember]:
        return await self.staff_members.list_by_tenant(tenant_id)

    async def update_staff_member(
            self,
            staff_member: StaffMember,
            data: StaffMemberUpdate
    ) -> StaffMember:
        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(staff_member, field, value)

            return staff_member


class ServiceManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.services = ServiceRepository(session)

    async def get_or_create_service(
            self,
            tenant_id: int,
            data: ServiceCreate
    ) -> Service:
        async with self.session.begin():
            service = await self.services.get_by_name_for_tenant(
                tenant_id=tenant_id,
                name=data.name,
            )
            if service is not None:
                return service

            service_data = data.model_dump()
            service = Service(
                tenant_id=tenant_id,
                **service_data,
            )
            await self.services.add(service)

        return service

    async def get_by_name_for_tenant(self, tenant_id: int, name: str) -> Service | None:
        return await self.services.get_by_name_for_tenant(
                tenant_id=tenant_id,
                name=name
            )

    async def list_by_tenant(self, tenant_id: int) -> list[Service]:
        return await self.services.list_by_tenant_id(tenant_id)

    async def update_service(
            self,
            service: Service,
            data: ServiceUpdate
    ) -> Service:
        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(service, field, value)

            return service

class StaffServices:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.staff_services = StaffServiceRepository(session)

    async def get_or_create_relation(
            self,
            *,
            staff_member_id: int,
            service_id: int
    ) -> StaffService:
        async with self.session.begin():
            staff_service = await self.staff_services.get_by_service_and_staff_member_id(
                staff_member_id=staff_member_id,
                service_id=service_id
            )

            if staff_service is not None:
                return staff_service

            staff_service = StaffService(
                staff_member_id=staff_member_id,
                service_id=service_id
            )
            await self.staff_services.add(staff_service)

        return staff_service