from fastapi import APIRouter, Depends, status

from sentio.api.deps import require_tenant_roles, get_current_tenant_user, get_booking_service
from sentio.core.enums import TenantUserRole, BookingStatus
from sentio.models.user import TenantUser
from sentio.schemas.booking import BookingCreate, BookingRead, BookingReschedule
from sentio.services.bookings import BookingService


router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate,
    booking_service: BookingService = Depends(get_booking_service),
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
):
    return await booking_service.create_booking(tenant_id=tenant_user.tenant_id, data=data)


@router.get("/{booking_id}", response_model=BookingRead, status_code=status.HTTP_200_OK)
async def get_booking(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
    tenant_user: TenantUser = Depends(get_current_tenant_user),
):
    return await booking_service.get_by_id_for_tenant(
        tenant_id=tenant_user.tenant_id, booking_id=booking_id
    )


@router.get(
    "/",
    response_model=list[BookingRead],
)
async def list_by_status(
    booking_status: BookingStatus,
    booking_service: BookingService = Depends(get_booking_service),
    tenant_user: TenantUser = Depends(get_current_tenant_user),
):
    return await booking_service.list_by_status(
        booking_status=booking_status, tenant_id=tenant_user.tenant_id
    )


@router.patch("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: int,
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
    booking_service: BookingService = Depends(get_booking_service),
):
    return await booking_service.cancel_booking(
        tenant_id=tenant_user.tenant_id, booking_id=booking_id
    )


@router.patch("/{booking_id}/reschedule", response_model=BookingRead)
async def reschedule_booking(
    booking_id: int,
    data: BookingReschedule,
    booking_service: BookingService = Depends(get_booking_service),
    tenant_user: TenantUser = Depends(
        require_tenant_roles(TenantUserRole.ADMIN, TenantUserRole.MANAGER, TenantUserRole.OWNER)
    ),
):
    return await booking_service.reschedule_booking_for_customer(
        tenant_id=tenant_user.tenant_id, booking_id=booking_id, data=data
    )
