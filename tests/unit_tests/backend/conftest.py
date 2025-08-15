import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.backend.config import settings
from src.backend.database import get_session
from src.backend.main import fastapi_app as original_app


@pytest_asyncio.fixture(scope="session")
async def create_test_engine_fixture():
    """
    테스트용 비동기 SQLAlchemy 엔진을 생성하고 세션 동안 유지합니다.
    """
    engine = create_async_engine(settings.EFFECTIVE_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def get_test_db_session_factory(create_test_engine_fixture):
    """
    테스트 세션 동안 사용할 비동기 세션 팩토리를 제공합니다.
    """
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(create_test_engine_fixture, class_=AsyncSession, expire_on_commit=False)
    yield async_session_maker

    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def get_test_db_session(get_test_db_session_factory):
    """
    각 테스트 함수마다 독립적인 데이터베이스 세션을 제공합니다.
    """
    async with get_test_db_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(get_test_db_session: AsyncSession):
    """
    각 테스트 함수마다 독립적인 FastAPI 테스트 클라이언트를 제공합니다.
    데이터베이스 세션은 `get_test_db_session` fixture를 통해 주입받습니다.
    """
    app = FastAPI()
    app.router.routes = original_app.router.routes

    async def get_session_override():
        yield get_test_db_session

    app.dependency_overrides[get_session] = get_session_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
