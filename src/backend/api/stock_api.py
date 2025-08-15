from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_session
from src.backend.models.stock import Stock, StockUpdate
from src.backend.services import stock_service

router = APIRouter()


@router.post("/stocks/", response_model=Stock)
async def create_stock(
    *,
    session: AsyncSession = Depends(get_session),
    stock: Stock,
) -> Stock:
    """
    Create a new stock entry.
    """
    return await stock_service.create_stock(session=session, stock=stock)


@router.get("/stocks/{stock_id}", response_model=Stock)
async def read_stock(
    *,
    session: AsyncSession = Depends(get_session),
    stock_id: int,
) -> Stock:
    """
    Get a stock by ID.
    """
    db_stock = await stock_service.get_stock(session=session, stock_id=stock_id)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock


@router.put("/stocks/{stock_id}", response_model=Stock)
async def update_stock(
    *,
    session: AsyncSession = Depends(get_session),
    stock_id: int,
    stock_update: StockUpdate,
) -> Stock:
    """
    Update a stock by ID.
    """
    db_stock = await stock_service.update_stock(
        session=session, stock_id=stock_id, stock_update=stock_update
    )
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock
