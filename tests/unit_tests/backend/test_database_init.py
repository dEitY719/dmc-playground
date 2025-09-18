"""
Tests for database initialization and session management.
"""

import pytest
import pytest_asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.types import DateTime, Float, String
from sqlmodel import SQLModel

from src.backend.database import get_db, init_db


@pytest_asyncio.fixture(scope="function")
async def engine_for_init_db_test(create_test_engine_fixture: AsyncEngine):
    """
    Provides a clean engine with no tables for init_db tests.
    """
    async with create_test_engine_fixture.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    yield create_test_engine_fixture
    async with create_test_engine_fixture.begin() as conn:
        # Recreate tables for other tests that might depend on them
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest.mark.asyncio
async def test_init_db_creates_tables(engine_for_init_db_test: AsyncEngine):
    """
    Tests if init_db successfully creates the 'stockinfo' and 'stockprice' tables.
    """
    async with engine_for_init_db_test.connect() as conn:

        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        # 1. Verify tables don't exist before init_db
        existing_tables = await conn.run_sync(get_tables)
        assert "stockinfo" not in existing_tables
        assert "stockprice" not in existing_tables

        # 2. Call init_db
        await init_db(async_engine=engine_for_init_db_test)

        # 3. Verify tables exist after init_db
        existing_tables = await conn.run_sync(get_tables)
        assert "stockinfo" in existing_tables
        assert "stockprice" in existing_tables


@pytest.mark.asyncio
async def test_stockinfo_table_columns(engine_for_init_db_test: AsyncEngine):
    """
    Tests if the 'stockinfo' table has the correct columns and primary key after init_db.
    """
    await init_db(async_engine=engine_for_init_db_test)
    async with engine_for_init_db_test.connect() as conn:

        def get_inspector_data(sync_conn):
            inspector = inspect(sync_conn)
            return {
                "columns": inspector.get_columns("stockinfo"),
                "pk": inspector.get_pk_constraint("stockinfo"),
            }

        inspector_data = await conn.run_sync(get_inspector_data)
        columns = inspector_data["columns"]
        pk_constraint = inspector_data["pk"]

        column_names = {col["name"] for col in columns}
        expected_columns = {"id", "ticker", "name", "market", "currency", "created_at", "updated_at"}
        assert expected_columns == column_names

        # Check column types
        ticker_col = next(c for c in columns if c["name"] == "ticker")
        assert isinstance(ticker_col["type"], String)
        assert not ticker_col["nullable"]

        # Check primary key
        assert pk_constraint["constrained_columns"] == ["id"]


@pytest.mark.asyncio
async def test_stockprice_table_columns(engine_for_init_db_test: AsyncEngine):
    """
    Tests if the 'stockprice' table has the correct columns and foreign key after init_db.
    """
    await init_db(async_engine=engine_for_init_db_test)
    async with engine_for_init_db_test.connect() as conn:

        def get_inspector_data(sync_conn):
            inspector = inspect(sync_conn)
            return {
                "columns": inspector.get_columns("stockprice"),
                "fk": inspector.get_foreign_keys("stockprice"),
            }

        inspector_data = await conn.run_sync(get_inspector_data)
        columns = inspector_data["columns"]
        foreign_keys = inspector_data["fk"]

        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "stock_info_id",
            "time",
            "open",
            "high",
            "low",
            "close",
            "previous_close",
            "change",
            "change_percent",
            "adjusted_close",
            "volume",
            "created_at",
            "updated_at",
        }
        assert expected_columns == column_names

        # Check column types
        time_col = next(c for c in columns if c["name"] == "time")
        assert isinstance(time_col["type"], DateTime)
        assert not time_col["nullable"]

        close_col = next(c for c in columns if c["name"] == "close")
        assert isinstance(close_col["type"], Float)
        assert not close_col["nullable"]

        # Check foreign key
        assert len(foreign_keys) == 1
        fk = foreign_keys[0]
        assert fk["constrained_columns"] == ["stock_info_id"]
        assert fk["referred_table"] == "stockinfo"
        assert fk["referred_columns"] == ["id"]


@pytest.mark.asyncio
async def test_get_db_yields_async_session() -> None:
    """
    Tests if get_db correctly yields an AsyncSession instance.
    """
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break
