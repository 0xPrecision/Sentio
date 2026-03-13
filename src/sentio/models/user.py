from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, String, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentio.core.enums import TenantUserRole
from sentio.models.database import Base, IDMixin, ISActiveMixin, TenantScopedMixin, TimestampMixin

if TYPE_CHECKING:
    from sentio.models.staff import StaffMember
    from sentio.models.tenant import Location, Tenant


class User(Base, IDMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    # ----- Relations -----
    tenant_users: Mapped[list["TenantUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    staff_members: Mapped[list["StaffMember"]] = relationship(
        back_populates="user",
    )


class TenantUser(Base, IDMixin, TenantScopedMixin, ISActiveMixin, TimestampMixin):
    __tablename__ = "tenant_users"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user_tenant_user"),)

    location_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("locations.id", ondelete="SET NULL")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[TenantUserRole] = mapped_column(
        Enum(TenantUserRole, name="tenant_user_role_enum"),
        default=TenantUserRole.STAFF,
        nullable=False,
    )

    # ----- Relations -----
    tenant: Mapped["Tenant"] = relationship(back_populates="tenant_users")
    user: Mapped["User"] = relationship(back_populates="tenant_users")
    location: Mapped["Location"] = relationship(back_populates="tenant_users")
