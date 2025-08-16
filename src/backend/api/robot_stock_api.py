from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.models.stock import Stock, StockUpdate
from src.backend.services import stock_service

stockbot_router = APIRouter(tags=["StockBot_API"])


@stockbot_router.post("/stocks/", response_model=Stock)
async def create_stock(
    *,
    session: AsyncSession = Depends(get_db),
    stock: Stock,
) -> Stock:
    """
    Create a new stock entry.
    """
    return await stock_service.create_stock(session=session, stock=stock)


@stockbot_router.get("/stocks/{stock_id}", response_model=Stock)
async def read_stock(
    *,
    session: AsyncSession = Depends(get_db),
    stock_id: int,
) -> Stock:
    """
    Get a stock by ID.
    """
    db_stock = await stock_service.get_stock(session=session, stock_id=stock_id)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock


@stockbot_router.get("/stocks/", response_model=list[Stock])
async def read_all_stocks(
    *,
    session: AsyncSession = Depends(get_db),
) -> list[Stock]:
    """
    Get all stock entries.
    """
    return await stock_service.get_all_stocks(session=session)


@stockbot_router.put("/stocks/{stock_id}", response_model=Stock)
async def update_stock(
    *,
    session: AsyncSession = Depends(get_db),
    stock_id: int,
    stock_update: StockUpdate,
) -> Stock:
    """
    Update a stock by ID.
    """
    db_stock = await stock_service.update_stock(session=session, stock_id=stock_id, stock_update=stock_update)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock


@stockbot_router.delete("/stocks/all")
async def delete_all_stocks(
    *,
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Delete all stock entries.
    """
    deleted_count = await stock_service.delete_all_stocks(session=session)
    return {"message": f"Successfully deleted {deleted_count} stocks"}


@stockbot_router.delete("/stocks/{stock_id}")
async def delete_stock(
    *,
    session: AsyncSession = Depends(get_db),
    stock_id: int,
) -> dict[str, str]:
    """
    Delete a stock by ID.
    """
    success = await stock_service.delete_stock(session=session, stock_id=stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"message": "Stock deleted successfully"}
