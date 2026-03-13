from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.exceptions import NotFoundError
from sentio.models.staff import StaffMember, StaffService
from sentio.repositories.services import ServiceRepository
from sentio.repositories.staff import (
    StaffMemberRepository,
    StaffServiceRepository,
)
from sentio.schemas.staff import StaffMemberCreate, StaffMemberUpdate


class StaffMemberService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.staff_members = StaffMemberRepository(session)

    async def create_staff_member(self, tenant_id: int, data: StaffMemberCreate) -> StaffMember:
        async with self.session.begin():
            staff_member_data = data.model_dump()

            staff_member = StaffMember(
                tenant_id=tenant_id,
                **staff_member_data,
            )
            await self.staff_members.add(staff_member)

        return staff_member

    async def get_by_name_for_tenant(self, tenant_id: int, display_name: str) -> StaffMember | None:
        return await self.staff_members.get_by_name_for_tenant(
            tenant_id=tenant_id, name=display_name
        )

    async def get_by_id_for_tenant(
        self, tenant_id: int, staff_member_id: int
    ) -> StaffMember | None:
        return await self.staff_members.get_by_id_for_tenant(
            tenant_id=tenant_id, staff_member_id=staff_member_id
        )

    async def list_by_tenant(self, tenant_id: int) -> list[StaffMember]:
        return await self.staff_members.list_by_tenant(tenant_id)

    async def update_staff_member(
        self, tenant_id: int, staff_member_id: int, data: StaffMemberUpdate
    ) -> StaffMember:
        async with self.session.begin():
            staff_member = await self.staff_members.get_by_id_for_tenant(
                tenant_id=tenant_id, staff_member_id=staff_member_id
            )
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(staff_member, field, value)

            return staff_member


class StaffServices:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.staff_services = StaffServiceRepository(session)
        self.staff_members = StaffMemberRepository(session)
        self.services = ServiceRepository(session)

    async def _ensure_staff_and_service(
        self, *, staff_member_id: int, tenant_id: int, service_id: int
    ):
        staff = await self.staff_members.get(staff_member_id)
        if staff is None or staff.tenant_id != tenant_id:
            raise NotFoundError("Staff member not found")

        svc = await self.services.get(service_id)
        if svc is None or svc.tenant_id != tenant_id:
            raise NotFoundError("Service not found")

        existing = await self.staff_services.get_by_keys(
            tenant_id=tenant_id, service_id=service_id, staff_member_id=staff_member_id
        )

        return existing

    async def create_relation(
        self, *, tenant_id: int, staff_member_id: int, service_id: int
    ) -> StaffService:
        existing = await self._ensure_staff_and_service(
            staff_member_id=staff_member_id, tenant_id=tenant_id, service_id=service_id
        )
        if existing:
            return existing

        async with self.session.begin():
            staff_service = StaffService(
                tenant_id=tenant_id, staff_member_id=staff_member_id, service_id=service_id
            )
            await self.staff_services.add(staff_service)

        return staff_service

    async def delete_relation(
        self, *, tenant_id: int, staff_member_id: int, service_id: int
    ) -> None:
        existing = await self._ensure_staff_and_service(
            tenant_id=tenant_id, staff_member_id=staff_member_id, service_id=service_id
        )
        if existing is None:
            return

        async with self.session.begin():
            await self.staff_services.delete(existing)
