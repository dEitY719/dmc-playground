"""
Tests for the new stock-related models.
"""

from datetime import datetime, timezone

import pytest
from pytest_asyncio import fixture as pytest_asyncio_fixture
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker
from sqlmodel import SQLModel, select

from src.backend.models.holding import StockHoldingDetail
from src.backend.models.stock import StockInfo
from src.backend.models.transaction import StockTransaction


# Fixture for an in-memory SQLite database for testing
@pytest_asyncio_fixture(name="session")
async def session_fixture():
    """
    Provides a test session for an in-memory SQLite database.
    """
    engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_stock_transaction(session: AsyncSession):
    """
    Test creating a StockTransaction entry.
    """
    stock_info = StockInfo(ticker="TEST_TR", name="Test Transaction Stock")
    session.add(stock_info)
    await session.commit()
    await session.refresh(stock_info)

    transaction = StockTransaction(
        user_id=1,
        stock_info_id=stock_info.id,
        transaction_date=datetime.now(timezone.utc),
        brokerage="Test Brokerage",
        transaction_type="매수",
        ticker="TEST_TR",
        transaction_price=100.0,
        quantity=10,
        total_amount=1000.0,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.user_id == 1
    assert transaction.stock_info_id == stock_info.id
    assert transaction.brokerage == "Test Brokerage"
    assert transaction.transaction_type == "매수"
    assert transaction.ticker == "TEST_TR"
    assert transaction.transaction_price == 100.0
    assert transaction.quantity == 10
    assert transaction.total_amount == 1000.0
    assert transaction.created_at is not None
    assert transaction.updated_at is not None


@pytest.mark.asyncio
async def test_create_stock_holding_detail(session: AsyncSession):
    """
    Test creating a StockHoldingDetail entry.
    """
    stock_info = StockInfo(ticker="TEST_HD", name="Test Holding Stock")
    session.add(stock_info)
    await session.commit()
    await session.refresh(stock_info)

    holding_detail = StockHoldingDetail(
        user_id=1,
        stock_info_id=stock_info.id,
        ticker="TEST_HD",
        holding_quantity=50,
        average_buy_price=120.0,
        total_buy_amount=6000.0,
        current_price=125.0,
        total_evaluation_amount=6250.0,
        total_profit=250.0,
        krw_profit=30000.0,
        daily_profit=100.0,
        current_exchange_rate=1300.0,
    )
    session.add(holding_detail)
    await session.commit()
    await session.refresh(holding_detail)

    assert holding_detail.id is not None
    assert holding_detail.user_id == 1
    assert holding_detail.stock_info_id == stock_info.id
    assert holding_detail.ticker == "TEST_HD"
    assert holding_detail.holding_quantity == 50
    assert holding_detail.average_buy_price == 120.0
    assert holding_detail.total_buy_amount == 6000.0
    assert holding_detail.current_price == 125.0
    assert holding_detail.total_evaluation_amount == 6250.0
    assert holding_detail.total_profit == 250.0
    assert holding_detail.krw_profit == 30000.0
    assert holding_detail.daily_profit == 100.0
    assert holding_detail.current_exchange_rate == 1300.0
    assert holding_detail.created_at is not None
    assert holding_detail.updated_at is not None


@pytest.mark.asyncio
async def test_stock_info_relationships(session: AsyncSession):
    """
    Test relationships between StockInfo and new models.
    """
    stock_info = StockInfo(ticker="REL_TEST", name="Relationship Test Stock")
    session.add(stock_info)
    await session.commit()
    await session.refresh(stock_info)

    transaction = StockTransaction(
        user_id=1,
        stock_info_id=stock_info.id,
        transaction_date=datetime.now(timezone.utc),
        brokerage="Rel Brokerage",
        transaction_type="매수",
        ticker="REL_TEST",
        transaction_price=50.0,
        quantity=5,
        total_amount=250.0,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    holding_detail = StockHoldingDetail(
        user_id=1,
        stock_info_id=stock_info.id,
        ticker="REL_TEST",
        holding_quantity=5,
        average_buy_price=50.0,
        total_buy_amount=250.0,
    )
    session.add(holding_detail)
    await session.commit()
    await session.refresh(holding_detail)

    # ✅ SQLAlchemy async 방식으로 관계까지 eager load
    result = await session.execute(
        select(StockInfo)
        .where(StockInfo.id == stock_info.id)
        .options(
            selectinload(StockInfo.transactions),
            selectinload(StockInfo.holding_details),
        )
    )
    stock_info_with_rels = result.scalar_one()

    assert len(stock_info_with_rels.transactions) == 1
    assert stock_info_with_rels.transactions[0].id == transaction.id
    assert len(stock_info_with_rels.holding_details) == 1
    assert stock_info_with_rels.holding_details[0].id == holding_detail.id


@pytest.mark.asyncio
async def test_stock_holding_detail_auto_update_on_transaction(session: AsyncSession):
    """
    Test automatic updates of StockHoldingDetail based on StockTransaction CRUD operations.
    """
    user_id = 1
    ticker = "AUTO_UPDATE"
    stock_info = StockInfo(ticker=ticker, name="Auto Update Stock")
    session.add(stock_info)
    await session.commit()
    await session.refresh(stock_info)

    stock_info_id = stock_info.id
    assert stock_info_id is not None

    # --- Scenario 1: Create a BUY transaction ---
    buy_transaction_1 = StockTransaction(
        user_id=user_id,
        stock_info_id=stock_info_id,
        transaction_date=datetime.now(timezone.utc),
        brokerage="BrokerA",
        transaction_type="매수",
        ticker=ticker,
        transaction_price=100.0,
        quantity=10,
        total_amount=1000.0,
    )
    session.add(buy_transaction_1)
    await session.commit()
    await session.refresh(buy_transaction_1)

    from src.backend.services.stock_service import _update_stock_holding_detail

    session.expire_all()  # ✅ await 제거
    session.add(stock_info)
    await _update_stock_holding_detail(session=session, user_id=user_id, stock_info_id=stock_info_id, ticker=ticker)

    result = await session.execute(
        select(StockHoldingDetail).where(
            StockHoldingDetail.user_id == user_id,
            StockHoldingDetail.stock_info_id == stock_info_id,
        )
    )
    holding_detail = result.scalars().first()

    assert holding_detail is not None
    assert holding_detail.holding_quantity == 10
    assert holding_detail.total_buy_amount == 1000.0
    assert holding_detail.average_buy_price == 100.0

    # --- Scenario 2: Add another BUY transaction ---
    buy_transaction_2 = StockTransaction(
        user_id=user_id,
        stock_info_id=stock_info_id,
        transaction_date=datetime.now(timezone.utc),
        brokerage="BrokerA",
        transaction_type="매수",
        ticker=ticker,
        transaction_price=120.0,
        quantity=10,
        total_amount=1200.0,
    )
    session.add(buy_transaction_2)
    await session.commit()
    await session.refresh(buy_transaction_2)

    session.expire_all()
    session.add(stock_info)
    await _update_stock_holding_detail(session=session, user_id=user_id, stock_info_id=stock_info_id, ticker=ticker)

    result = await session.execute(
        select(StockHoldingDetail).where(
            StockHoldingDetail.user_id == user_id,
            StockHoldingDetail.stock_info_id == stock_info_id,
        )
    )
    holding_detail = result.scalars().first()

    assert holding_detail is not None
    assert holding_detail.holding_quantity == 20
    assert holding_detail.total_buy_amount == 2200.0  # 1000 + 1200
    assert holding_detail.average_buy_price == 110.0  # 2200 / 20

    # --- Scenario 3: Create a SELL transaction ---
    sell_transaction_1 = StockTransaction(
        user_id=user_id,
        stock_info_id=stock_info_id,
        transaction_date=datetime.now(timezone.utc),
        brokerage="BrokerA",
        transaction_type="매도",
        ticker=ticker,
        transaction_price=130.0,
        quantity=5,
        total_amount=650.0,
    )
    session.add(sell_transaction_1)
    await session.commit()
    await session.refresh(sell_transaction_1)

    session.expire_all()
    session.add(stock_info)
    await _update_stock_holding_detail(session=session, user_id=user_id, stock_info_id=stock_info_id, ticker=ticker)

    result = await session.execute(
        select(StockHoldingDetail).where(
            StockHoldingDetail.user_id == user_id,
            StockHoldingDetail.stock_info_id == stock_info_id,
        )
    )
    holding_detail = result.scalars().first()

    assert holding_detail is not None
    assert holding_detail.holding_quantity == 15  # 20 - 5
    assert holding_detail.total_buy_amount == 1550.0  # 2200 - 650
    assert holding_detail.average_buy_price == pytest.approx(103.33333333333333)

    # --- Scenario 4: Sell all remaining stock ---
    sell_transaction_2 = StockTransaction(
        user_id=user_id,
        stock_info_id=stock_info_id,
        transaction_date=datetime.now(timezone.utc),
        brokerage="BrokerA",
        transaction_type="매도",
        ticker=ticker,
        transaction_price=150.0,
        quantity=15,
        total_amount=2250.0,
    )
    session.add(sell_transaction_2)
    await session.commit()
    await session.refresh(sell_transaction_2)

    session.expire_all()
    session.add(stock_info)
    await _update_stock_holding_detail(session=session, user_id=user_id, stock_info_id=stock_info_id, ticker=ticker)

    result = await session.execute(
        select(StockHoldingDetail).where(
            StockHoldingDetail.user_id == user_id,
            StockHoldingDetail.stock_info_id == stock_info_id,
        )
    )
    holding_detail = result.scalars().first()

    assert holding_detail is None  # Should be deleted when quantity is 0
