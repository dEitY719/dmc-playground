from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from src.backend.config import settings

engine: AsyncEngine = create_async_engine(
    settings.EFFECTIVE_DATABASE_URL,
    echo=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db(async_engine: AsyncEngine = engine) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
