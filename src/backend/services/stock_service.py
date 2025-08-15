from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.backend.models.stock import Stock


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
