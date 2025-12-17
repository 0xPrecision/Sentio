from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.customer import Customer, TenantCustomer
from sentio.repositories.customers import CustomerRepository, TenantCustomerRepository
from sentio.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    TenantCustomerCreate,
    TenantCustomerUpdatePayment,
)


class CustomerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customers = CustomerRepository(session)

    async def get_or_create_customer(self, data: CustomerCreate) -> Customer:
        async with self.session.begin():
            customer: Customer | None = None

            if data.phone is not None:
                customer = await self.customers.get_by_phone(data.phone)
            if customer is None and data.telegram_id is not None:
                customer = await self.customers.get_by_telegram_id(data.telegram_id)

            if customer is None:
                create_data = data.model_dump()
                customer = Customer(**create_data)
                await self.customers.add(customer)

        return customer

    async def get_by_phone(self, phone: str) -> Customer | None:
        return await self.customers.get_by_phone(phone)

    async def get_by_telegram_id(self, telegram_id: int) -> Customer | None:
        return await self.customers.get_by_telegram_id(telegram_id)

    async def update_customer(self, customer: Customer, data: CustomerUpdate) -> Customer:
        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(customer, field, value)

            return customer


class TenantCustomerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tenant_customers = TenantCustomerRepository(session)

    async def get_or_create_tenant_customer(self, data: TenantCustomerCreate) -> TenantCustomer:
        async with self.session.begin():
            tenant_customer = await self.tenant_customers.get_by_tenant_and_customer(
                tenant_id=data.tenant_id, customer_id=data.customer_id
            )
            if tenant_customer is not None:
                return tenant_customer

            create_data = data.model_dump()
            tenant_customer = TenantCustomer(**create_data)
            await self.tenant_customers.add(tenant_customer)

        return tenant_customer

    async def get_by_tenant_and_customer_id(
        self, tenant_id: int, customer_id: int
    ) -> TenantCustomer | None:
        return await self.tenant_customers.get_by_tenant_and_customer(
            tenant_id=tenant_id, customer_id=customer_id
        )

    async def list_by_tenant(self, tenant_id: int) -> list[TenantCustomer]:
        return await self.tenant_customers.list_by_tenant(tenant_id)

    async def update_tenant_customer_payment(
        self, tenant_customer: TenantCustomer, data: TenantCustomerUpdatePayment
    ) -> TenantCustomer:
        async with self.session.begin():
            update_data = data.model_dump()

            for field, value in update_data.items():
                setattr(tenant_customer, field, value)

            return tenant_customer
