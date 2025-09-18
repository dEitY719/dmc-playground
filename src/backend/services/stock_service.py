"""
Service layer for stock-related business logic.
"""

from datetime import datetime, timezone
from typing import Any, cast

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.backend.models.stock import (
    StockInfo,
    StockInfoCreate,
    StockInfoRead,
    StockInfoReadWithPrices,
    StockInfoUpdate,
    StockPrice,
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
