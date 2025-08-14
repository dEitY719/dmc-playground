from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.backend.config import settings
from src.backend.database import get_session
from src.backend.main import fastapi_app
from src.backend.models.stock import Stock  # Stock 모델 임포트

# ✅ PostgreSQL 테스트 DB 엔진 생성
engine = create_async_engine(
    settings.EFFECTIVE_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan manager for tests: create all tables before tests and drop them after.
    """
    print("Lifespan: Creating tables in test DB...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    print("Lifespan: Dropping tables in test DB...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# ✅ lifespan을 테스트 전용으로 오버라이드
fastapi_app.lifespan = test_lifespan


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency override to use the test database session.
    """
    async with async_session_maker() as session:
        yield session


# ✅ DI 오버라이드
fastapi_app.dependency_overrides[get_session] = override_get_session


# @pytest_asyncio.fixture(name="client")
# async def client_fixture() -> AsyncGenerator[AsyncClient, None]:
#     """
#     Create an AsyncClient for the FastAPI app, ensuring lifespan events are handled.
#     """
#     async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
#         yield client


@pytest_asyncio.fixture(name="client")
async def client_fixture() -> AsyncClient:
    """
    AsyncClient fixture that manually triggers FastAPI lifespan events
    for httpx versions without lifespan support.
    """
    # lifespan 수동 실행
    async with fastapi_app.router.lifespan_context(fastapi_app):
        async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
            yield client
