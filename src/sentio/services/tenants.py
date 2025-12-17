from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.enums import TenantUserRole
from sentio.models.tenant import Location, Tenant
from sentio.models.user import TenantUser
from sentio.repositories.tenants import LocationRepository, TenantRepository, TenantUserRepository
from sentio.schemas.tenant import (
    LocationCreate,
    LocationUpdate,
    TenantCreateWithLocation,
    TenantUpdate,
    TenantUserCreate,
    TenantUserUpdate,
)


class TenantService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tenants = TenantRepository(session)
        self.locations = LocationRepository(session)

    async def create_tenant_with_default_location(self, data: TenantCreateWithLocation) -> Tenant:
        async with self.session.begin():
            tenant_data = data.model_dump(
                exclude={"default_location_name", "address", "description", "slug"}
            )

            tenant = Tenant(**tenant_data, slug=data.slug.lower(), is_active=True)
            await self.tenants.add(tenant)

            location = Location(
                tenant=tenant,
                name=data.default_location_name,
                address=data.address,
                description=data.description,
                is_default=True,
            )
            await self.locations.add(location)

        return tenant

    async def get_tenant_by_id(self, tenant_id: int) -> Tenant | None:
        return await self.tenants.get(tenant_id)

    async def get_tenant_by_slug(self, slug: str) -> Tenant | None:
        return await self.tenants.get_by_slug(slug.lower())

    async def update_tenant(self, tenant: Tenant, data: TenantUpdate) -> Tenant:
        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            slug = update_data.pop("slug", None)
            if slug is not None:
                tenant.slug = slug.lower()

            for field, value in update_data.items():
                setattr(tenant, field, value)

            return tenant


class LocationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.locations = LocationRepository(session)

    async def get_or_create_location(self, tenant_id: int, data: LocationCreate) -> Location:
        async with self.session.begin():
            location = await self.locations.get_by_name(tenant_id, data.name.lower())
            if location is not None:
                return location

            location = Location(
                tenant_id=tenant_id,
                name=data.name,
                address=data.address,
                description=data.description,
                is_default=data.is_default,
            )
            await self.locations.add(location)

        return location

    async def get_by_name(self, tenant_id: int, name: str) -> Location | None:
        return await self.locations.get_by_name(tenant_id, name)

    async def update_location(self, location: Location, data: LocationUpdate) -> Location:
        async with self.session.begin():
            location_data = data.model_dump(exclude_unset=True)

            for field, value in location_data.items():
                setattr(location, field, value)

            return location


class TenantUserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tenant_users = TenantUserRepository(session)

    async def get_or_create_tenant_user(self, tenant_id: int, data: TenantUserCreate) -> TenantUser:
        async with self.session.begin():
            tenant_user = await self.tenant_users.get_by_user(
                tenant_id=tenant_id, user_id=data.user_id
            )
            if tenant_user is not None:
                return tenant_user

            tenant_user_data = data.model_dump()

            tenant_user = TenantUser(tenant_id=tenant_id, **tenant_user_data)

            await self.tenant_users.add(tenant_user)

        return tenant_user

    async def get_by_user(self, tenant_id: int, user_id: int) -> TenantUser | None:
        return await self.tenant_users.get_by_user(tenant_id=tenant_id, user_id=user_id)

    async def list_by_role(self, tenant_id: int, role: TenantUserRole) -> list[TenantUser]:
        return await self.tenant_users.list_by_role(tenant_id, role)

    async def update_tenant_user(
        self, tenant_user: TenantUser, data: TenantUserUpdate
    ) -> TenantUser:
        async with self.session.begin():
            tenant_user_data = data.model_dump(exclude_unset=True, exclude={"user_id"})

            for field, value in tenant_user_data.items():
                setattr(tenant_user, field, value)

            return tenant_user
