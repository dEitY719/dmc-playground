from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.backend.models.stock import Stock, StockCreate, StockRead, StockUpdate
from src.backend.services.yf_adapter import df_to_stockbase


async def create_stock(*, session: AsyncSession, stock: StockCreate) -> StockRead:
    """
    Creates a new stock entry in the database.
    """
    db_stock = Stock.model_validate(stock)
    session.add(db_stock)
    await session.commit()
    await session.refresh(db_stock)
    return StockRead.model_validate(db_stock)


async def get_stock(*, session: AsyncSession, stock_id: int) -> Stock | None:
    """
    Retrieves a stock entry by its ID.
    """
    result = await session.execute(select(Stock).where(Stock.id == stock_id))
    return result.scalar_one_or_none()


async def get_all_stocks(*, session: AsyncSession) -> list[StockRead]:
    """
    Retrieves all stock entries from the database.
    """
    result = await session.execute(select(Stock))
    return [StockRead.model_validate(stock) for stock in result.scalars().all()]


async def update_stock(*, session: AsyncSession, stock_id: int, stock_update: StockUpdate) -> StockRead | None:
    """
    Updates an existing stock entry in the database.
    """
    # Retrieve the actual Stock object from the database
    result = await session.execute(select(Stock).where(Stock.id == stock_id))
    db_stock = result.scalar_one_or_none()

    if not db_stock:
        return None

    # Update model fields
    update_data = stock_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_stock, key, value)

    # Manually update the updated_at timestamp
    db_stock.updated_at = datetime.now(timezone.utc)

    session.add(db_stock)
    await session.commit()
    await session.refresh(db_stock)
    return StockRead.model_validate(db_stock)


async def delete_stock(*, session: AsyncSession, stock_id: int) -> bool:
    """
    Deletes a stock entry from the database.
    Returns True if deletion was successful, False otherwise.
    """
    db_stock = await get_stock(session=session, stock_id=stock_id)
    if not db_stock:
        return False

    await session.delete(db_stock)
    await session.commit()
    return True


async def delete_all_stocks(*, session: AsyncSession) -> int:
    """
    Deletes all stock entries from the database.
    Returns the number of deleted rows.
    """
    result = await session.execute(select(Stock))
    stocks_to_delete = result.scalars().all()
    deleted_count = 0
    for stock in stocks_to_delete:
        await session.delete(stock)
        deleted_count += 1
    await session.commit()
    return deleted_count


async def upsert_stocks_from_dataframe(*, session: AsyncSession, df, ticker: str, name: str | None = None, market: str | None = None, currency: str = "USD", auto_adjust: bool = True, timezone: str = "UTC") -> int:
    """
    yfinance DataFrame을 받아 표준 모델로 변환 후 DB에 저장합니다.
    현재는 단순 add_all(insert)만 수행하고, 동일 키 중복 방지는 호출측에서 보장한다고 가정합니다.
    반환값은 저장된 레코드 수입니다.
    """
    records = df_to_stockbase(df, ticker=ticker, name=name, market=market, currency=currency, auto_adjust=auto_adjust, timezone=timezone)
    for record in records:
        session.add(Stock.model_validate(record))
    await session.commit()
    return len(records)
