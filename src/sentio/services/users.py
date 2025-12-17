from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.user import User
from sentio.repositories.users import UserRepository
from sentio.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def get_or_create_user(
            self,
            data: UserCreate
    ) -> User:
        async with self.session.begin():
            user = await self.users.get_by_email(data.email)
            if user is not None:
                return user

            create_data = data.model_dump()
            user = User(
                **create_data
            )
            await self.users.add(user)

        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self.users.get_by_email(email.lower())

    async def update_user(
            self,
            user: User,
            data: UserUpdate
    ) -> User:
        async with self.session.begin():
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(user, field, value)

        return user