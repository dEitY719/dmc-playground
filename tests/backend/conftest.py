from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.backend.database import get_session
from src.backend.main import fastapi_app

# Use an async SQLite database for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    """
    Test lifespan manager to create and drop database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


fastapi_app.router.lifespan_context = test_lifespan


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency override to provide a test database session.
    """
    async with async_session_maker() as session:
        yield session


fastapi_app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(name="client")
async def client_fixture() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an AsyncClient for the FastAPI app.
    """
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
