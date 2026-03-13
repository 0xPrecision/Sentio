from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.staff import StaffMember, StaffService
from sentio.repositories.base import BaseRepository


class StaffMemberRepository(BaseRepository[StaffMember]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StaffMember)

    async def get_by_name_for_tenant(self, *, tenant_id: int, name: str) -> StaffMember | None:
        stmt = select(StaffMember).where(
            StaffMember.tenant_id == tenant_id, StaffMember.display_name == name
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_tenant(
        self, *, tenant_id: int, staff_member_id: int
    ) -> StaffMember | None:
        stmt = select(StaffMember).where(
            StaffMember.tenant_id == tenant_id, StaffMember.id == staff_member_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: int, active_only: bool = False) -> list[StaffMember]:
        stmt = select(StaffMember).where(StaffMember.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(StaffMember.tenant_id == tenant_id, StaffMember.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StaffServiceRepository(BaseRepository[StaffService]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StaffService)

    async def get_by_keys(
        self, *, service_id: int, staff_member_id: int, tenant_id: int
    ) -> StaffService | None:
        stmt = select(StaffService).where(
            StaffService.service_id == service_id,
            StaffService.staff_member_id == staff_member_id,
            StaffService.tenant_id == tenant_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
