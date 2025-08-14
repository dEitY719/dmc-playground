from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from src.backend.config import settings

# ✅ pytest 실행 여부에 따라 DATABASE_URL 또는 TEST_DATABASE_URL 사용
engine: AsyncEngine = create_async_engine(
    settings.EFFECTIVE_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 연결 확인 옵션 추가
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session for each request.
    """
    async with async_session_maker() as session:
        yield session


async def create_db_and_tables() -> None:
    """
    Utility function to create all database tables defined by SQLModel models.
    This should be called once when the application starts.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
