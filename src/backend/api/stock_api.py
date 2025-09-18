"""
API routes for stock data.
"""

import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db, reset_db
from src.backend.models.stock import (
    StockInfoCreate,
    StockInfoRead,
    StockInfoReadWithPrices,
    StockInfoUpdate,
)
from src.backend.services import stock_service

router = APIRouter(prefix="/stock", tags=["stock"])


@router.post("/info/", response_model=StockInfoRead)
async def create_stock_info(stock_info: StockInfoCreate, db: AsyncSession = Depends(get_db)) -> StockInfoRead:
    """
    Creates a new stock info entry.
    Note: The main way to create stock data is via the /download endpoint.
    This endpoint is for manually adding a stock's metadata.
    """
    db_stock_info = await stock_service.get_or_create_stock_info(
        session=db, ticker=stock_info.ticker, stock_info_data=stock_info.model_dump()
    )
    return StockInfoRead.model_validate(db_stock_info)


@router.get("/info/id/{stock_info_id}", response_model=StockInfoReadWithPrices)
async def read_stock_info(stock_info_id: int, db: AsyncSession = Depends(get_db)) -> StockInfoReadWithPrices:
    """
    Reads a stock info entry by its ID, including all associated price data.
    """
    db_stock_info = await stock_service.get_stock_info(session=db, stock_info_id=stock_info_id)
    if db_stock_info is None:
        raise HTTPException(status_code=404, detail="Stock info not found")
    return db_stock_info


@router.get("/info/ticker/{ticker}", response_model=StockInfoReadWithPrices)
async def read_stock_info_by_ticker(ticker: str, db: AsyncSession = Depends(get_db)) -> StockInfoReadWithPrices:
    """
    Reads a stock info entry by its ticker, including all associated price data.
    """
    db_stock_info = await stock_service.get_stock_info_by_ticker(session=db, ticker=ticker)
    if not db_stock_info:
        raise HTTPException(status_code=404, detail=f"Stock info with ticker '{ticker}' not found")
    return db_stock_info


@router.get("/info/", response_model=list[StockInfoRead])
async def read_all_stock_infos(db: AsyncSession = Depends(get_db)) -> list[StockInfoRead]:
    """
    Reads all stock info entries, without price data for performance.
    """
    return await stock_service.get_all_stock_infos(session=db)


@router.put("/info/{stock_info_id}", response_model=StockInfoRead)
async def update_stock_info(
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


@router.delete("/info/{stock_info_id}", response_model=dict)
async def delete_stock_info(stock_info_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    """
    Deletes a stock info entry and all its associated price data.
    """
    success = await stock_service.delete_stock_info(session=db, stock_info_id=stock_info_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock info not found")
    return {"ok": True}


class DownloadRequest(BaseModel):
    ticker: str
    start: str
    end: str
    auto_adjust: bool = True
    timezone: str = "UTC"
    name: str | None = None
    market: str | None = None
    currency: str = "USD"


@router.post("/download", response_model=dict)
async def download_and_store(req: DownloadRequest, db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    """
    Downloads historical stock data from yfinance and stores it in the database.
    Creates StockInfo if it doesn't exist, and adds new StockPrice entries.
    """
    df = yf.download(req.ticker, start=req.start, end=req.end, auto_adjust=req.auto_adjust)
    if df is None or len(df) == 0:
        return {"saved": 0}
    saved_count = await stock_service.upsert_stocks_from_dataframe(
        session=db,
        df=df,
        ticker=req.ticker,
        name=req.name,
        market=req.market,
        currency=req.currency,
        auto_adjust=req.auto_adjust,
        timezone=req.timezone,
    )
    return {"saved": saved_count}


@router.post("/reset", response_model=dict)
async def reset_database() -> dict[str, bool]:
    """
    Resets the entire database by dropping and recreating all tables.
    """
    await reset_db()
    return {"ok": True}
