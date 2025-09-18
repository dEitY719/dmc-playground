from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from src.backend.config import settings
from src.backend.database import get_db
from src.backend.main import app as main_app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test session.
    """
    import asyncio

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def create_test_engine_fixture() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create a test database engine.
    Using NullPool to prevent connection issues across test functions.
    """
    engine = create_async_engine(settings.EFFECTIVE_DATABASE_URL, echo=False, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def get_test_db_session(create_test_engine_fixture: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for each test function.
    This fixture ensures that each test runs in isolation by creating and dropping tables for each test.
    """
    async_session_maker = async_sessionmaker(
        bind=create_test_engine_fixture, class_=AsyncSession, expire_on_commit=False
    )

    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(get_test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a new FastAPI test client for each test function.
    This client uses the isolated database session provided by the `get_test_db_session` fixture.
    """

    def get_session_override() -> AsyncSession:
        return get_test_db_session

    main_app.dependency_overrides[get_db] = get_session_override

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up the override after the test
    main_app.dependency_overrides.clear()
