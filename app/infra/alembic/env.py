import os, logging
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from app.infra.db import NAMING  # твой MetaData

config = context.config
target_metadata = NAMING

# safe logging init
try:
    if config.config_file_name:
        fileConfig(config.config_file_name, disable_existing_loggers=False)
except Exception:
    logging.basicConfig(level=logging.INFO)

ASYNC_DB_URL = os.environ["DATABASE_URL"]  # postgresql+asyncpg://...

def run_migrations_offline():
    url = ASYNC_DB_URL.replace("+asyncpg", "")
    context.configure(url=url, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def _run_sync(connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    engine = create_async_engine(ASYNC_DB_URL, poolclass=pool.NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(_run_sync)

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())