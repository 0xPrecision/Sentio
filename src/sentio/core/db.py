from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from sentio.core.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    url=settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_pre_ping=True
)

SessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session