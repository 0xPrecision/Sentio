from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.customer import Customer, TenantCustomer
from sentio.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_phone(self, phone_number: str) -> Customer | None:
        stmt = select(Customer).where(Customer.phone == phone_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> Customer | None:
        stmt = select(Customer).where(Customer.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TenantCustomerRepository(BaseRepository[TenantCustomer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TenantCustomer)

    async def get_by_tenant_and_customer(
        self, *, tenant_id: int, customer_id: int
    ) -> TenantCustomer | None:
        stmt = select(TenantCustomer).where(
            TenantCustomer.tenant_id == tenant_id,
            TenantCustomer.customer_id == customer_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: int, active_only: bool = False
    ) -> list[TenantCustomer]:
        stmt = select(TenantCustomer).where(TenantCustomer.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(TenantCustomer.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
