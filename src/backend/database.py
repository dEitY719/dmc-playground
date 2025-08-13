from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.backend.config import settings

# The async database engine is created once and used throughout the application
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session for each request.
    """
    async with async_session_maker() as session:
        yield session


async def create_db_and_tables() -> None:  # Added return type
    """
    Utility function to create all database tables defined by SQLModel models.
    This should be called once when the application starts.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
