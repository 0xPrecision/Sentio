from fastapi import APIRouter, Depends, status

from sentio.api.deps import require_tenant_roles, get_schedule_service, get_current_tenant_user
from sentio.core.enums import TenantUserRole
from sentio.models.user import TenantUser
from sentio.schemas.work_schedules import WorkScheduleRead, WorkScheduleCreate, WorkScheduleUpdate
from sentio.services.work_schedules import WorkScheduleService


router = APIRouter(prefix="/work-schedules", tags=["work-schedules"])


@router.get("/{schedule_id}", response_model=WorkScheduleRead, status_code=status.HTTP_200_OK)
async def get_schedule(
    schedule_id: int,
    tenant_user: TenantUser = Depends(get_current_tenant_user),
    schedule_service: WorkScheduleService = Depends(get_schedule_service),
):
    return await schedule_service.get_work_schedule(
        schedule_id=schedule_id,
        tenant_id=tenant_user.tenant_id,
    )


@router.post("/", response_model=WorkScheduleRead, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: WorkScheduleCreate,
    schedule_service: WorkScheduleService = Depends(get_schedule_service),
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
):
    return await schedule_service.create_work_schedule(tenant_id=tenant_user.tenant_id, data=data)


@router.patch(
    "/{schedule_id}",
    response_model=WorkScheduleRead,
)
async def update_schedule(
    schedule_id: int,
    data: WorkScheduleUpdate,
    schedule_service: WorkScheduleService = Depends(get_schedule_service),
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
):
    return await schedule_service.update_work_schedule(
        schedule_id=schedule_id, tenant_id=tenant_user.tenant_id, data=data
    )
