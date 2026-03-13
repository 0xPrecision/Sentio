from collections.abc import AsyncGenerator, Callable, Awaitable

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.core.db import SessionFactory
from sentio.core.config import get_settings
from sentio.core.enums import TenantUserRole
from sentio.models.tenant import Tenant
from sentio.models.user import User, TenantUser
from sentio.services.bookings import WorkScheduleService, TimeSlotService, BookingService
from sentio.services.services import ServiceManager
from sentio.services.staff import StaffMemberService, StaffServices

security = HTTPBearer(auto_error=False)


def get_settings_dep():
    return get_settings()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    session: AsyncSession = Depends(get_db_session),
    settings=Depends(get_settings_dep),
) -> User:
    if creds is None:
        raise _unauthorized()

    token = creds.credentials.strip()
    if not token:
        raise _unauthorized()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            options={"require": ["exp", "sub"]},
        )
    except JWTError:
        raise _unauthorized("Invalid token")

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise _unauthorized("Invalid token payload")

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise _unauthorized("User inactive")

    return user


async def get_current_tenant_user(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    x_tenant_slug: str | None = Header(default=None, alias="X-Tenant-Slug"),
) -> TenantUser:
    if x_tenant_slug is None:
        raise HTTPException(status_code=400, detail="X-Tenant-Slug header required")

    stmt = (
        select(TenantUser)
        .join(Tenant, Tenant.id == TenantUser.tenant_id)
        .where(
            TenantUser.user_id == user.id,
            Tenant.slug == x_tenant_slug,
            TenantUser.is_active.is_(True),
            Tenant.is_active.is_(True),
        )
    )
    res = await session.execute(stmt)
    tenant_user = res.scalar_one_or_none()

    if tenant_user is None:
        raise HTTPException(status_code=403, detail="No access to tenant")

    return tenant_user


def get_service_manager(session: AsyncSession = Depends(get_db_session)) -> ServiceManager:
    return ServiceManager(session=session)


def get_staff_member_service(session: AsyncSession = Depends(get_db_session)) -> StaffMemberService:
    return StaffMemberService(session=session)


def get_staff_services(session: AsyncSession = Depends(get_db_session)) -> StaffServices:
    return StaffServices(session=session)


def get_schedule_service(session: AsyncSession = Depends(get_db_session)) -> WorkScheduleService:
    return WorkScheduleService(session=session)


def get_time_slot_service(session: AsyncSession = Depends(get_db_session)) -> TimeSlotService:
    return TimeSlotService(session=session)


def get_booking_service(session: AsyncSession = Depends(get_db_session)) -> BookingService:
    return BookingService(session=session)


def require_platform_admin(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_platform_admin:
        raise HTTPException(status_code=403, detail="Platform admin required")
    return user


def require_tenant_roles(*allowed: TenantUserRole) -> Callable[..., Awaitable[TenantUser]]:
    async def _dep(
        tenant_user: TenantUser = Depends(get_current_tenant_user),
    ) -> TenantUser:
        if tenant_user.role not in allowed:
            allowed_str = ", ".join(str(r.value) for r in allowed)
            raise HTTPException(status_code=403, detail=f"Role required: {allowed_str}")
        return tenant_user

    return _dep
