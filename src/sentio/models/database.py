from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый declarative-класс для всех ORM-моделей."""

    pass


class TimestampMixin:
    """Стандартные поля created_at/updated_at для сущностей."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class IDMixin:
    """Стандартное поле id для сущностей."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class ISActiveMixin:
    """Стандартное поле is_active для сущностей."""

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class TenantScopedMixin:
    """Стандартное поле tenant_id для сущностей."""

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
