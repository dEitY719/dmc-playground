"""
API routes for stock data.
"""

import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db, reset_db
from src.backend.models.holding import (
    StockHoldingDetailCreate,
    StockHoldingDetailRead,
    StockHoldingDetailUpdate,
)
from src.backend.models.stock import (
    StockInfoCreate,
    StockInfoRead,
    StockInfoReadWithPrices,
    StockInfoUpdate,
)
from src.backend.models.transaction import (
    StockTransactionCreate,
    StockTransactionRead,
    StockTransactionUpdate,
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


# -------------------------
# StockTransaction Endpoints
# -------------------------
@router.post("/transaction/", response_model=StockTransactionRead)
async def create_stock_transaction(
    transaction: StockTransactionCreate, db: AsyncSession = Depends(get_db)
) -> StockTransactionRead:
    """
    Creates a new stock transaction entry.
    """
    db_transaction = await stock_service.create_stock_transaction(session=db, transaction=transaction)
    return db_transaction


@router.get("/transaction/{transaction_id}", response_model=StockTransactionRead)
async def read_stock_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)) -> StockTransactionRead:
    """
    Reads a stock transaction entry by its ID.
    """
    db_transaction = await stock_service.get_stock_transaction(session=db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Stock transaction not found")
    return db_transaction


@router.get("/transaction/user/{user_id}", response_model=list[StockTransactionRead])
async def read_user_stock_transactions(user_id: int, db: AsyncSession = Depends(get_db)) -> list[StockTransactionRead]:
    """
    Reads all stock transaction entries for a specific user.
    """
    return await stock_service.get_user_stock_transactions(session=db, user_id=user_id)


@router.put("/transaction/{transaction_id}", response_model=StockTransactionRead)
async def update_stock_transaction(
    transaction_id: int, transaction: StockTransactionUpdate, db: AsyncSession = Depends(get_db)
) -> StockTransactionRead:
    """
    Updates an existing stock transaction entry.
    """
    db_transaction = await stock_service.update_stock_transaction(
        session=db, transaction_id=transaction_id, transaction_update=transaction
    )
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Stock transaction not found")
    return db_transaction


@router.delete("/transaction/{transaction_id}", response_model=dict)
async def delete_stock_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    """
    Deletes a stock transaction entry.
    """
    success = await stock_service.delete_stock_transaction(session=db, transaction_id=transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock transaction not found")
    return {"ok": True}


# --------------------------
# StockHoldingDetail Endpoints
# --------------------------
@router.post("/holding/", response_model=StockHoldingDetailRead)
async def create_stock_holding_detail(
    holding_detail: StockHoldingDetailCreate, db: AsyncSession = Depends(get_db)
) -> StockHoldingDetailRead:
    """
    Creates a new stock holding detail entry.
    """
    db_holding_detail = await stock_service.create_stock_holding_detail(session=db, holding_detail=holding_detail)
    return db_holding_detail


@router.get("/holding/{holding_id}", response_model=StockHoldingDetailRead)
async def read_stock_holding_detail(holding_id: int, db: AsyncSession = Depends(get_db)) -> StockHoldingDetailRead:
    """
    Reads a stock holding detail entry by its ID.
    """
    db_holding_detail = await stock_service.get_stock_holding_detail(session=db, holding_id=holding_id)
    if db_holding_detail is None:
        raise HTTPException(status_code=404, detail="Stock holding detail not found")
    return db_holding_detail


@router.get("/holding/user/{user_id}", response_model=list[StockHoldingDetailRead])
async def read_user_stock_holding_details(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> list[StockHoldingDetailRead]:
    """
    Reads all stock holding detail entries for a specific user.
    """
    return await stock_service.get_user_stock_holding_details(session=db, user_id=user_id)


@router.get("/holding/user/{user_id}/ticker/{ticker}", response_model=StockHoldingDetailRead)
async def read_user_stock_holding_detail_by_ticker(
    user_id: int, ticker: str, db: AsyncSession = Depends(get_db)
) -> StockHoldingDetailRead:
    """
    Reads a stock holding detail entry for a specific user and ticker.
    """
    db_holding_detail = await stock_service.get_user_stock_holding_detail_by_ticker(
        session=db, user_id=user_id, ticker=ticker
    )
    if db_holding_detail is None:
        raise HTTPException(status_code=404, detail="Stock holding detail not found")
    return db_holding_detail


@router.put("/holding/{holding_id}", response_model=StockHoldingDetailRead)
async def update_stock_holding_detail(
    holding_id: int, holding_detail: StockHoldingDetailUpdate, db: AsyncSession = Depends(get_db)
) -> StockHoldingDetailRead:
    """
    Updates an existing stock holding detail entry.
    """
    db_holding_detail = await stock_service.update_stock_holding_detail(
        session=db, holding_id=holding_id, holding_detail_update=holding_detail
    )
    if db_holding_detail is None:
        raise HTTPException(status_code=404, detail="Stock holding detail not found")
    return db_holding_detail


@router.delete("/holding/{holding_id}", response_model=dict)
async def delete_stock_holding_detail(holding_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    """
    Deletes a stock holding detail entry.
    """
    success = await stock_service.delete_stock_holding_detail(session=db, holding_id=holding_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock holding detail not found")
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
