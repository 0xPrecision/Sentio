from fastapi import APIRouter, Depends, status, Response

from sentio.api.deps import (
    require_tenant_roles,
    get_current_tenant_user,
    get_staff_member_service,
    get_staff_services,
)
from sentio.core.enums import TenantUserRole
from sentio.models.user import TenantUser
from sentio.schemas.staff import (
    StaffMemberRead,
    StaffMemberCreate,
    StaffMemberUpdate,
    StaffServiceRead,
)
from sentio.services.staff import StaffMemberService, StaffServices

router = APIRouter(prefix="/staff", tags=["staff"])


@router.post(
    "/",
    response_model=StaffMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_staff_member(
    data: StaffMemberCreate,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    staff_member_service: StaffMemberService = Depends(get_staff_member_service),
):
    return await staff_member_service.create_staff_member(
        tenant_id=tenant_user.tenant_id, data=data
    )


@router.post(
    "/{staff_id}/services/{service_id}",
    response_model=StaffServiceRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_service_to_staff_member(
    staff_id: int,
    service_id: int,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    staff_services: StaffServices = Depends(get_staff_services),
):
    return await staff_services.create_relation(
        tenant_id=tenant_user.tenant_id, staff_member_id=staff_id, service_id=service_id
    )


@router.delete(
    "/{staff_id}/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_from_staff_member(
    staff_id: int,
    service_id: int,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    staff_services: StaffServices = Depends(get_staff_services),
) -> Response:
    await staff_services.delete_relation(
        tenant_id=tenant_user.tenant_id, staff_member_id=staff_id, service_id=service_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{staff_id}",
    response_model=StaffMemberRead,
    status_code=status.HTTP_200_OK,
)
async def get_staff_member(
    staff_id: int,
    tenant_user: TenantUser = Depends(get_current_tenant_user),
    staff_member_service: StaffMemberService = Depends(get_staff_member_service),
):
    return await staff_member_service.get_by_id_for_tenant(
        tenant_id=tenant_user.tenant_id, staff_member_id=staff_id
    )


@router.get(
    "/",
    response_model=list[StaffMemberRead],
)
async def list_staff_members(
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    staff_member_service: StaffMemberService = Depends(get_staff_member_service),
):
    return await staff_member_service.list_by_tenant(tenant_id=tenant_user.tenant_id)


@router.patch(
    "/{staff_id}",
    response_model=StaffMemberRead,
    status_code=status.HTTP_200_OK,
)
async def update_staff_member(
    data: StaffMemberUpdate,
    staff_id: int,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    staff_member_service: StaffMemberService = Depends(get_staff_member_service),
):
    return await staff_member_service.update_staff_member(
        tenant_id=tenant_user.tenant_id, staff_member_id=staff_id, data=data
    )
