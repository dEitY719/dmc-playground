"""
Service layer for stock-related business logic.
"""

from datetime import datetime, timezone
from typing import Any, cast

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.backend.models.holding import (
    StockHoldingDetail,
    StockHoldingDetailCreate,
    StockHoldingDetailRead,
    StockHoldingDetailUpdate,
)
from src.backend.models.price import StockPrice
from src.backend.models.stock import (
    StockInfo,
    StockInfoCreate,
    StockInfoRead,
    StockInfoReadWithPrices,
    StockInfoUpdate,
)
from src.backend.models.transaction import (
    StockTransaction,
    StockTransactionCreate,
    StockTransactionRead,
    StockTransactionUpdate,
)
from src.backend.services.yf_adapter import df_to_stockbase


async def get_or_create_stock_info(*, session: AsyncSession, ticker: str, stock_info_data: dict) -> StockInfo:
    """
    Retrieves a StockInfo by ticker or creates it if it doesn't exist.
    """
    result = await session.execute(select(StockInfo).where(StockInfo.ticker == ticker))
    db_stock_info = result.scalar_one_or_none()
    if not db_stock_info:
        db_stock_info = StockInfo.model_validate(StockInfoCreate(**stock_info_data))
        session.add(db_stock_info)
        await session.commit()
        await session.refresh(db_stock_info)
    return db_stock_info


async def get_stock_info(*, session: AsyncSession, stock_info_id: int) -> StockInfoReadWithPrices | None:
    """
    Retrieves a stock info entry by its ID with all its prices, using eager loading.
    """
    result = await session.execute(
        select(StockInfo).where(StockInfo.id == stock_info_id).options(selectinload(cast(Any, StockInfo.prices)))
    )
    stock_info = result.scalar_one_or_none()
    if not stock_info:
        return None
    return StockInfoReadWithPrices.model_validate(stock_info)


async def get_stock_info_by_ticker(*, session: AsyncSession, ticker: str) -> StockInfoReadWithPrices | None:
    """
    Retrieves a stock info entry by its ticker with all its prices, using eager loading.
    """
    result = await session.execute(
        select(StockInfo).where(StockInfo.ticker == ticker).options(selectinload(cast(Any, StockInfo.prices)))
    )
    stock_info = result.scalar_one_or_none()
    if not stock_info:
        return None
    return StockInfoReadWithPrices.model_validate(stock_info)


async def get_all_stock_infos(*, session: AsyncSession) -> list[StockInfoRead]:
    """
    Retrieves all stock info entries from the database, without prices.
    """
    result = await session.execute(select(StockInfo))
    return [StockInfoRead.model_validate(stock) for stock in result.scalars().all()]


# ----------------------------
# StockTransaction Service Functions
# ----------------------------
async def create_stock_transaction(
    *, session: AsyncSession, transaction: StockTransactionCreate
) -> StockTransactionRead:
    """
    Creates a new stock transaction entry.
    """
    db_transaction = StockTransaction.model_validate(transaction)
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    # Update StockHoldingDetail based on the new transaction
    await _update_stock_holding_detail(
        session=session,
        user_id=db_transaction.user_id,
        stock_info_id=db_transaction.stock_info_id,
        ticker=db_transaction.ticker,
    )

    return db_transaction


async def get_stock_transaction(*, session: AsyncSession, transaction_id: int) -> StockTransactionRead | None:
    """
    Retrieves a stock transaction entry by its ID.
    """
    result = await session.execute(select(StockTransaction).where(StockTransaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        return None
    return transaction


async def get_user_stock_transactions(*, session: AsyncSession, user_id: int) -> list[StockTransactionRead]:
    """
    Retrieves all stock transaction entries for a specific user.
    """
    result = await session.execute(select(StockTransaction).where(StockTransaction.user_id == user_id))
    return [StockTransactionRead.model_validate(t) for t in result.scalars().all()]


async def update_stock_transaction(
    *, session: AsyncSession, transaction_id: int, transaction_update: StockTransactionUpdate
) -> StockTransactionRead | None:
    """
    Updates an existing stock transaction entry.
    """
    result = await session.execute(select(StockTransaction).where(StockTransaction.id == transaction_id))
    db_transaction = result.scalar_one_or_none()

    if not db_transaction:
        return None

    update_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)

    db_transaction.updated_at = datetime.now(timezone.utc)
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    # Update StockHoldingDetail after transaction update
    await _update_stock_holding_detail(
        session=session,
        user_id=db_transaction.user_id,
        stock_info_id=db_transaction.stock_info_id,
        ticker=db_transaction.ticker,
    )

    return db_transaction


async def delete_stock_transaction(*, session: AsyncSession, transaction_id: int) -> bool:
    """
    Deletes a stock transaction entry.
    """
    result = await session.execute(select(StockTransaction).where(StockTransaction.id == transaction_id))
    db_transaction = result.scalar_one_or_none()

    if not db_transaction:
        return False

    await session.delete(db_transaction)
    await session.commit()

    # Update StockHoldingDetail after transaction deletion
    await _update_stock_holding_detail(
        session=session,
        user_id=db_transaction.user_id,
        stock_info_id=db_transaction.stock_info_id,
        ticker=db_transaction.ticker,
    )

    return True


async def update_stock_info(
    *, session: AsyncSession, stock_info_id: int, stock_update: StockInfoUpdate
) -> StockInfoRead | None:
    """
    Updates an existing stock info entry in the database.
    """
    result = await session.execute(select(StockInfo).where(StockInfo.id == stock_info_id))
    db_stock_info = result.scalar_one_or_none()

    if not db_stock_info:
        return None

    update_data = stock_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_stock_info, key, value)

    db_stock_info.updated_at = datetime.now(timezone.utc)
    session.add(db_stock_info)
    await session.commit()
    await session.refresh(db_stock_info)
    return StockInfoRead.model_validate(db_stock_info)


async def delete_stock_info(*, session: AsyncSession, stock_info_id: int) -> bool:
    """
    Deletes a stock info and its associated prices from the database.
    """
    result = await session.execute(select(StockInfo).where(StockInfo.id == stock_info_id))
    db_stock_info = result.scalar_one_or_none()

    if not db_stock_info:
        return False

    # Delete associated prices first
    price_result = await session.execute(select(StockPrice).where(StockPrice.stock_info_id == stock_info_id))
    for price in price_result.scalars().all():
        await session.delete(price)

    await session.delete(db_stock_info)
    await session.commit()
    return True


async def upsert_stocks_from_dataframe(
    *,
    session: AsyncSession,
    df: pd.DataFrame,
    ticker: str,
    name: str | None = None,
    market: str | None = None,
    currency: str = "USD",
    auto_adjust: bool = True,
    timezone: str = "UTC",
) -> int:
    """
    Converts a yfinance DataFrame to standard models and saves them to the DB.
    Skips duplicate records (based on time and ticker) and only saves new data.
    Returns the number of newly saved records.
    """
    stock_info_data = {"ticker": ticker, "name": name, "market": market, "currency": currency}
    stock_info = await get_or_create_stock_info(session=session, ticker=ticker, stock_info_data=stock_info_data)
    assert stock_info.id is not None, "StockInfo must have an ID after creation"

    records = df_to_stockbase(
        df, ticker=ticker, name=name, market=market, currency=currency, auto_adjust=auto_adjust, timezone=timezone
    )

    if not records:
        return 0

    times = [r.time for r in records]
    min_time, max_time = min(times), max(times)

    existing = await session.execute(
        select(StockPrice.time).where(
            StockPrice.stock_info_id == stock_info.id,
            StockPrice.time >= min_time,
            StockPrice.time <= max_time,
        )
    )
    existing_times = set(existing.scalars().all())

    inserted_count = 0
    for record in records:
        if record.time not in existing_times:
            price_data = record.model_dump()
            # Remove fields that are not in StockPrice
            price_data.pop("ticker", None)
            price_data.pop("name", None)
            price_data.pop("market", None)
            price_data.pop("currency", None)

            db_price = StockPrice(**price_data, stock_info_id=stock_info.id)
            session.add(db_price)
            inserted_count += 1

    if inserted_count > 0:
        await session.commit()

    return inserted_count


# ----------------------------
# StockHoldingDetail Service Functions
# ----------------------------
async def create_stock_holding_detail(
    *, session: AsyncSession, holding_detail: StockHoldingDetailCreate
) -> StockHoldingDetailRead:
    """
    Creates a new stock holding detail entry.
    """
    db_holding_detail = StockHoldingDetail.model_validate(holding_detail)
    session.add(db_holding_detail)
    await session.commit()
    await session.refresh(db_holding_detail)
    return db_holding_detail


async def get_stock_holding_detail(*, session: AsyncSession, holding_id: int) -> StockHoldingDetailRead | None:
    """
    Retrieves a stock holding detail entry by its ID.
    """
    result = await session.execute(select(StockHoldingDetail).where(StockHoldingDetail.id == holding_id))
    holding_detail = result.scalar_one_or_none()
    if not holding_detail:
        return None
    return holding_detail


async def get_user_stock_holding_details(*, session: AsyncSession, user_id: int) -> list[StockHoldingDetailRead]:
    """
    Retrieves all stock holding detail entries for a specific user.
    """
    result = await session.execute(select(StockHoldingDetail).where(StockHoldingDetail.user_id == user_id))
    return [StockHoldingDetailRead.model_validate(h) for h in result.scalars().all()]


async def _update_stock_holding_detail(*, session: AsyncSession, user_id: int, stock_info_id: int, ticker: str) -> None:
    """
    Calculates and updates the StockHoldingDetail for a given user and stock based on all transactions.
    """
    # 1. Get all transactions for the user and stock
    result = await session.execute(
        select(StockTransaction).where(
            StockTransaction.user_id == user_id, StockTransaction.stock_info_id == stock_info_id
        )
    )
    transactions = result.scalars().all()

    # 2. Calculate holding quantity, total buy amount, and average buy price
    holding_quantity = 0
    total_buy_amount = 0.0

    for t in transactions:
        if t.transaction_type == "매수":
            holding_quantity += t.quantity
            total_buy_amount += t.total_amount
        elif t.transaction_type == "매도":
            holding_quantity -= t.quantity
            total_buy_amount -= t.total_amount  # Adjust total_buy_amount for sales

    average_buy_price = total_buy_amount / holding_quantity if holding_quantity > 0 else 0.0

    # 3. Get or create StockHoldingDetail
    result = await session.execute(
        select(StockHoldingDetail).where(
            StockHoldingDetail.user_id == user_id, StockHoldingDetail.stock_info_id == stock_info_id
        )
    )
    db_holding_detail = result.scalar_one_or_none()

    if holding_quantity <= 0:
        if db_holding_detail:
            await session.delete(db_holding_detail)
            await session.commit()
        return

    if db_holding_detail:
        # Update existing
        db_holding_detail.holding_quantity = holding_quantity
        db_holding_detail.average_buy_price = average_buy_price
        db_holding_detail.total_buy_amount = total_buy_amount
        db_holding_detail.updated_at = datetime.now(timezone.utc)
        session.add(db_holding_detail)
    else:
        # Create new
        new_holding_detail = StockHoldingDetailCreate(
            user_id=user_id,
            stock_info_id=stock_info_id,
            ticker=ticker,
            holding_quantity=holding_quantity,
            average_buy_price=average_buy_price,
            total_buy_amount=total_buy_amount,
        )
        db_holding_detail = StockHoldingDetail.model_validate(new_holding_detail)
        session.add(db_holding_detail)

    await session.commit()
    await session.refresh(db_holding_detail)


async def get_user_stock_holding_detail_by_ticker(
    *, session: AsyncSession, user_id: int, ticker: str
) -> StockHoldingDetailRead | None:
    """
    Retrieves a stock holding detail entry for a specific user and ticker.
    """
    result = await session.execute(
        select(StockHoldingDetail).where(StockHoldingDetail.user_id == user_id, StockHoldingDetail.ticker == ticker)
    )
    holding_detail = result.scalar_one_or_none()
    if not holding_detail:
        return None
    return holding_detail


async def update_stock_holding_detail(
    *, session: AsyncSession, holding_id: int, holding_detail_update: StockHoldingDetailUpdate
) -> StockHoldingDetailRead | None:
    """
    Updates an existing stock holding detail entry.
    """
    result = await session.execute(select(StockHoldingDetail).where(StockHoldingDetail.id == holding_id))
    db_holding_detail = result.scalar_one_or_none()

    if not db_holding_detail:
        return None

    update_data = holding_detail_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_holding_detail, key, value)

    db_holding_detail.updated_at = datetime.now(timezone.utc)
    session.add(db_holding_detail)
    await session.commit()
    await session.refresh(db_holding_detail)
    return db_holding_detail


async def delete_stock_holding_detail(*, session: AsyncSession, holding_id: int) -> bool:
    """
    Deletes a stock holding detail entry.
    """
    result = await session.execute(select(StockHoldingDetail).where(StockHoldingDetail.id == holding_id))
    db_holding_detail = result.scalar_one_or_none()

    if not db_holding_detail:
        return False

    await session.delete(db_holding_detail)
    await session.commit()
    return True
