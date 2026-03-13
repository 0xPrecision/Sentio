from fastapi import APIRouter, Depends, status

from sentio.api.deps import require_tenant_roles, get_current_tenant_user, get_time_slot_service
from sentio.core.enums import TenantUserRole
from sentio.models.user import TenantUser
from sentio.schemas.time_slots import TimeSlotRead, TimeSlotCreate
from sentio.services.time_slots import TimeSlotService


router = APIRouter(prefix="/time-slots", tags=["time-slots"])


@router.get("/{time_slot_id}", response_model=TimeSlotRead, status_code=status.HTTP_200_OK)
async def get_time_slot(
    time_slot_id: int,
    time_slot_service: TimeSlotService = Depends(get_time_slot_service),
    tenant_user: TenantUser = Depends(get_current_tenant_user),
):
    return await time_slot_service.get_available_slot(
        tenant_id=tenant_user.tenant_id, time_slot_id=time_slot_id
    )


@router.post("/", response_model=TimeSlotRead, status_code=status.HTTP_201_CREATED)
async def create_time_slot(
    data: TimeSlotCreate,
    time_slot_service: TimeSlotService = Depends(get_time_slot_service),
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
):
    return await time_slot_service.create_slot(tenant_id=tenant_user.tenant_id, data=data)
