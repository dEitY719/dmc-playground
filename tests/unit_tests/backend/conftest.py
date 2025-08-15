import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel

from src.backend.main import fastapi_app as original_app
from src.backend.database import get_session
from src.backend.config import settings


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    각 테스트 함수마다 독립적인 FastAPI 테스트 클라이언트와 데이터베이스 세션을 제공합니다.
    테스트 시작 전에 데이터베이스를 초기화하고, 테스트 종료 후에 정리합니다.
    """
    engine = create_async_engine(settings.EFFECTIVE_DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    app = FastAPI()
    app.router.routes = original_app.router.routes

    async def get_test_session():
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.rollback()
                # async with 블록이 종료될 때 세션이 닫히거나 Connection Pool에 반환됩니다.

    app.dependency_overrides[get_session] = get_test_session

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac

    await engine.dispose()

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
