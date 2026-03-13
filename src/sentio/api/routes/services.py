from fastapi import APIRouter, Depends, status, Query

from sentio.api.deps import require_tenant_roles, get_current_tenant_user, get_service_manager
from sentio.core.enums import TenantUserRole
from sentio.models.user import TenantUser
from sentio.schemas.services import ServiceCreate, ServiceRead, ServiceUpdate
from sentio.services.services import ServiceManager


router = APIRouter(prefix="/services", tags=["services"])


@router.post(
    "/",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    data: ServiceCreate,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    service_manager: ServiceManager = Depends(get_service_manager),
):
    return await service_manager.create_service(tenant_id=tenant_user.tenant_id, data=data)


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
    status_code=status.HTTP_200_OK,
)
async def get_service(
    service_id: int,
    tenant_user: TenantUser = Depends(get_current_tenant_user),
    service_manager: ServiceManager = Depends(get_service_manager),
):
    return await service_manager.get_by_id_for_tenant(
        tenant_id=tenant_user.tenant_id, service_id=service_id
    )


@router.get(
    "/",
    response_model=list[ServiceRead],
)
async def list_services(
    tenant_user: TenantUser = Depends(get_current_tenant_user),
    service_manager: ServiceManager = Depends(get_service_manager),
    location_id: int | None = Query(default=None, description="Filter services by location"),
):
    return await service_manager.list_by_tenant_with_location(
        tenant_id=tenant_user.tenant_id, location_id=location_id
    )


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
    status_code=status.HTTP_200_OK,
)
async def update_service(
    data: ServiceUpdate,
    service_id: int,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    service_manager: ServiceManager = Depends(get_service_manager),
):
    return await service_manager.update_service(
        service_id=service_id, tenant_id=tenant_user.tenant_id, data=data
    )
