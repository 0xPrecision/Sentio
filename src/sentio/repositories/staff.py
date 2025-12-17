from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.staff import StaffMember, Service, StaffService
from sentio.repositories.base import BaseRepository


class StaffMemberRepository(BaseRepository[StaffMember]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StaffMember)

    async def get_by_name_for_tenant(self, *, tenant_id: int, name: str) -> StaffMember | None:
        stmt = select(StaffMember).where(
            StaffMember.tenant_id == tenant_id,
            StaffMember.display_name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(self,
                               tenant_id: int,
                               active_only: bool = False
                               ) -> list[StaffMember]:
        stmt = select(StaffMember).where(StaffMember.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(
                StaffMember.tenant_id == tenant_id,
                StaffMember.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Service)

    async def get_by_name_for_tenant(self, *, name: str, tenant_id: int) -> Service | None:
        stmt = select(Service).where(
            Service.tenant_id == tenant_id,
            Service.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant_id(self, tenant_id: int) -> list[Service]:
        stmt = select(Service).where(Service.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StaffServiceRepository(BaseRepository[StaffService]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StaffService)

    async def get_by_service_and_staff_member_id(
            self,
            service_id: int,
            staff_member_id: int
    ) -> StaffService | None:
        stmt = select(StaffService).where(
            StaffService.service_id == service_id,
            StaffService.staff_member_id == staff_member_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()