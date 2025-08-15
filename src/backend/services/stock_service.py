from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.backend.models.stock import Stock, StockUpdate


async def create_stock(*, session: AsyncSession, stock: Stock) -> Stock:
    """
    Creates a new stock entry in the database.
    """
    db_stock = Stock.model_validate(stock)
    session.add(db_stock)
    await session.commit()
    await session.refresh(db_stock)
    return db_stock


async def get_stock(*, session: AsyncSession, stock_id: int) -> Stock | None:
    """
    Retrieves a stock entry by its ID.
    """
    result = await session.execute(select(Stock).where(Stock.id == stock_id))
    return result.scalar_one_or_none()


async def update_stock(*, session: AsyncSession, stock_id: int, stock_update: StockUpdate) -> Stock | None:
    """
    Updates an existing stock entry in the database.
    """
    db_stock = await get_stock(session=session, stock_id=stock_id)
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
    return db_stock
