from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentio.models.user import User
from sentio.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str, only_active: bool = False) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        if only_active:
            stmt = stmt.where(User.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
