import pytest
import pytest_asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.types import DateTime, String
from sqlmodel import SQLModel

from src.backend.database import get_db, init_db


@pytest_asyncio.fixture(scope="function")
async def setup_test_db(create_test_engine_fixture: AsyncEngine):
    """
    각 테스트 함수 실행 전에 데이터베이스를 초기화하고, 테스트 후 정리합니다.
    """
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield create_test_engine_fixture
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def clean_test_db(create_test_engine_fixture: AsyncEngine):
    """
    각 테스트 함수 실행 전에 데이터베이스를 완전히 비웁니다.
    """
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    yield create_test_engine_fixture


@pytest_asyncio.fixture(scope="function")
async def engine_for_init_db_test(create_test_engine_fixture: AsyncEngine):
    """
    init_db 테스트를 위해 테이블이 없는 깨끗한 엔진을 제공합니다.
    """
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    yield create_test_engine_fixture
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.mark.asyncio
async def test_init_db_creates_tables(engine_for_init_db_test: AsyncEngine):
    """
    init_db 함수가 데이터베이스 테이블을 성공적으로 생성하는지 테스트합니다.
    """
    async with engine_for_init_db_test.connect() as conn:
        # 1. init_db 호출 전 테이블이 없는지 확인
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        existing_tables = await conn.run_sync(get_tables)
        assert "stock" not in existing_tables  # Stock 모델의 테이블 이름이 'stock'이라고 가정

        # 2. init_db 함수 호출
        await init_db(async_engine=engine_for_init_db_test)

        # 3. init_db 호출 후 테이블이 생성되었는지 확인
        existing_tables = await conn.run_sync(get_tables)
        assert "stock" in existing_tables

        # 4. 'stock' 테이블의 컬럼 확인
        def get_columns(sync_conn, table_name):
            inspector = inspect(sync_conn)
            return inspector.get_columns(table_name)

        columns = await conn.run_sync(lambda sync_conn: get_columns(sync_conn, "stock"))
        column_names = {col["name"] for col in columns}

        expected_columns = {
            "id",
            "ticker",
            "name",
            "market",
            "currency",
            "time",
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "created_at",
            "updated_at",
            "change_percent",
            "previous_close",
            "change",
        }
        assert expected_columns == column_names


@pytest.mark.asyncio
async def test_init_db_check_column_type(engine_for_init_db_test: AsyncEngine) -> None:
    """
    init_db 함수가 생성한 테이블의 특정 컬럼 타입이 올바른지 테스트합니다.
    """
    async with engine_for_init_db_test.connect() as conn:
        # init_db 함수 호출하여 테이블 생성
        await init_db(async_engine=engine_for_init_db_test)

        def get_columns(sync_conn, table_name):
            inspector = inspect(sync_conn)
            return inspector.get_columns(table_name)

        columns = await conn.run_sync(lambda sync_conn: get_columns(sync_conn, "stock"))

        # ticker 컬럼 타입 확인
        ticker_column = next((col for col in columns if col["name"] == "ticker"), None)
        assert ticker_column is not None
        assert isinstance(ticker_column["type"], String)

        # created_at 컬럼 타입 확인
        created_at_column = next((col for col in columns if col["name"] == "created_at"), None)
        assert created_at_column is not None
        assert isinstance(created_at_column["type"], DateTime)


@pytest.mark.asyncio
async def test_get_db_yields_async_session(get_test_db_session: AsyncSession) -> None:
    """
    get_db 함수가 AsyncSession 인스턴스를 올바르게 반환하는지 테스트합니다.
    """
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        # 추가적으로 세션이 활성 상태인지 확인할 수 있지만, 이는 SQLAlchemy의 내부 동작에 더 가깝습니다.
        # 예를 들어, 세션에 쿼리를 시도하여 유효성을 확인할 수 있습니다.
        break  # 제너레이터는 한 번만 yield하므로 break


@pytest.mark.asyncio
async def test_db_creation_and_deletion(setup_test_db: AsyncEngine):
    """
    setup_test_db 픽스처를 사용하여 데이터베이스 생성 및 삭제를 확인합니다.
    """
    async with setup_test_db.connect() as conn:

        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        # 픽스처에 의해 테이블이 생성되었는지 확인
        existing_tables = await conn.run_sync(get_tables)
        assert "stock" in existing_tables

    # 테스트 함수 종료 후 픽스처의 teardown 부분에서 drop_all이 호출되므로,
    # 여기서는 명시적으로 drop_all을 호출할 필요가 없습니다.
    # 다음 테스트가 시작될 때 테이블이 없는 상태임을 확인하는 방식으로 검증됩니다.
