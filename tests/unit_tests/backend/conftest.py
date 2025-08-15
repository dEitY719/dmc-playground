import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.backend.config import settings
from src.backend.database import get_session
from src.backend.main import fastapi_app as original_app


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    각 테스트 함수마다 독립적인 FastAPI 테스트 클라이언트와 데이터베이스 세션을 제공합니다.
    테스트 시작 전에 데이터베이스를 초기화하고, 테스트 종료 후에 정리합니다.
    """
    engine = create_async_engine(settings.EFFECTIVE_DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        app = FastAPI()
        app.router.routes = original_app.router.routes

        async def get_test_session():
            async with async_session_maker() as session:
                yield session

        app.dependency_overrides[get_session] = get_test_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    finally:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        await engine.dispose()
