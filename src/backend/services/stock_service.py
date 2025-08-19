from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.backend.models.stock import Stock, StockCreate, StockRead, StockUpdate


async def create_stock(*, session: AsyncSession, stock: StockCreate) -> StockRead:
    """
    Creates a new stock entry in the database.
    """
    db_stock = Stock.model_validate(stock)
    session.add(db_stock)
    await session.commit()
    await session.refresh(db_stock)
    return StockRead.model_validate(db_stock)


async def get_stock(*, session: AsyncSession, stock_id: int) -> StockRead | None:
    """
    Retrieves a stock entry by its ID.
    """
    result = await session.execute(select(Stock).where(Stock.id == stock_id))
    db_stock = result.scalar_one_or_none()
    if db_stock:
        return StockRead.model_validate(db_stock)
    return None


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
