"""
Tests for the new stock-related models.
"""

from datetime import datetime, timezone

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.backend.models.holding import StockHoldingDetail
from src.backend.models.stock import StockInfo
from src.backend.models.transaction import StockTransaction


# Fixture for an in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    """
    Provides a test session for an in-memory SQLite database.
    """
    engine = create_engine("sqlite:///./test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_create_stock_transaction(session: Session):
    """
    Test creating a StockTransaction entry.
    """
    stock_info = StockInfo(ticker="TEST_TR", name="Test Transaction Stock")
    session.add(stock_info)
    session.commit()
    session.refresh(stock_info)

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
    session.commit()
    session.refresh(transaction)

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


def test_create_stock_holding_detail(session: Session):
    """
    Test creating a StockHoldingDetail entry.
    """
    stock_info = StockInfo(ticker="TEST_HD", name="Test Holding Stock")
    session.add(stock_info)
    session.commit()
    session.refresh(stock_info)

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
    session.commit()
    session.refresh(holding_detail)

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


def test_stock_info_relationships(session: Session):
    """
    Test relationships between StockInfo and new models.
    """
    stock_info = StockInfo(ticker="REL_TEST", name="Relationship Test Stock")
    session.add(stock_info)
    session.commit()
    session.refresh(stock_info)

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
    session.commit()
    session.refresh(transaction)

    holding_detail = StockHoldingDetail(
        user_id=1,
        stock_info_id=stock_info.id,
        ticker="REL_TEST",
        holding_quantity=5,
        average_buy_price=50.0,
        total_buy_amount=250.0,
    )
    session.add(holding_detail)
    session.commit()
    session.refresh(holding_detail)
    session.refresh(stock_info)

    assert len(stock_info.transactions) == 1
    assert stock_info.transactions[0].id == transaction.id
    assert len(stock_info.holding_details) == 1
    assert stock_info.holding_details[0].id == holding_detail.id
