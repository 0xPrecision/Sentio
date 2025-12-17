import enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.tenant import Location, Tenant
from sentio.models.user import TenantUser
from sentio.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Tenant)

    async def get_by_slug(self, slug: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.slug == slug.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Location)

    async def get_by_name(self, tenant_id: int, name: str) -> Location | None:
        stmt = select(Location).where(
            Location.tenant_id == tenant_id, Location.name == name.lower()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: int) -> list[Location]:
        stmt = select(Location).where(Location.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class TenantUserRepository(BaseRepository[TenantUser]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TenantUser)

    async def get_by_user(self, *, tenant_id: int, user_id: int) -> TenantUser | None:
        stmt = select(TenantUser).where(
            TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_role(self, tenant_id: int, role: enum.Enum) -> list[TenantUser]:
        stmt = select(TenantUser).where(
            TenantUser.tenant_id == tenant_id,
            TenantUser.role == role,
            TenantUser.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
