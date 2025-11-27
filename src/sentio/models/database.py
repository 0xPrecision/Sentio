import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sentio.core.config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,
)

async_session = async_sessionmaker(bind=async_engine)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow
    )
