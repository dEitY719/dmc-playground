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


async def reset_db(async_engine: AsyncEngine = engine) -> None:
    """
    개발/테스트 용: 모든 테이블 드롭 후 최신 모델로 재생성.
    프로덕션에서는 마이그레이션 도구(Alembic) 사용 권장.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
