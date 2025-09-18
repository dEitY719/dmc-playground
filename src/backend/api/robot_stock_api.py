"""
API routes for robot stock data, simplified for specific automated tasks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.models.stock import (
    StockInfoCreate,
    StockInfoRead,
    StockInfoReadWithPrices,
    StockInfoUpdate,
)
from src.backend.services import stock_service

stockbot_router = APIRouter(prefix="/robot/stocks", tags=["robot-stocks"])


@stockbot_router.post("/", response_model=StockInfoRead)
async def create_stock_info_robot(stock_info: StockInfoCreate, db: AsyncSession = Depends(get_db)) -> StockInfoRead:
    """
    Creates a stock info entry.
    """
    db_stock_info = await stock_service.get_or_create_stock_info(
        session=db, ticker=stock_info.ticker, stock_info_data=stock_info.model_dump()
    )
    return StockInfoRead.model_validate(db_stock_info)


@stockbot_router.get("/{ticker}", response_model=StockInfoReadWithPrices)
async def read_stock_info_by_ticker_robot(ticker: str, db: AsyncSession = Depends(get_db)) -> StockInfoReadWithPrices:
    """
    Reads stock info and prices for a given ticker.
    """
    db_stock_info = await stock_service.get_stock_info_by_ticker(session=db, ticker=ticker)
    if not db_stock_info:
        raise HTTPException(status_code=404, detail=f"Stock info with ticker '{ticker}' not found")
    return db_stock_info


@stockbot_router.get("/", response_model=list[StockInfoRead])
async def read_all_stock_infos_robot(db: AsyncSession = Depends(get_db)) -> list[StockInfoRead]:
    """
    Reads all stock info entries (without prices).
    """
    return await stock_service.get_all_stock_infos(session=db)


@stockbot_router.put("/{stock_info_id}", response_model=StockInfoRead)
async def update_stock_info_robot(
    stock_info_id: int, stock_info: StockInfoUpdate, db: AsyncSession = Depends(get_db)
) -> StockInfoRead:
    """
    Updates a stock info entry.
    """
    db_stock_info = await stock_service.update_stock_info(
        session=db, stock_info_id=stock_info_id, stock_update=stock_info
    )
    if db_stock_info is None:
        raise HTTPException(status_code=404, detail="Stock info not found")
    return db_stock_info


@stockbot_router.delete("/{stock_info_id}", response_model=dict)
async def delete_stock_info_robot(stock_info_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    """
    Deletes a stock info entry and all its associated prices.
    """
    success = await stock_service.delete_stock_info(session=db, stock_info_id=stock_info_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock info not found")
    return {"ok": True}
