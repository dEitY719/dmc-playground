import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db, reset_db
from src.backend.models.stock import StockCreate, StockRead, StockUpdate
from src.backend.services import stock_service

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/", response_model=StockRead)
async def create_stock(stock: StockCreate, db: AsyncSession = Depends(get_db)) -> StockRead:
    return await stock_service.create_stock(session=db, stock=stock)


@router.get("/{stock_id}", response_model=StockRead)
async def read_stock(stock_id: int, db: AsyncSession = Depends(get_db)) -> StockRead:
    db_stock = await stock_service.get_stock(session=db, stock_id=stock_id)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return StockRead.model_validate(db_stock)


@router.get("/", response_model=list[StockRead])
async def read_stocks(db: AsyncSession = Depends(get_db)) -> list[StockRead]:
    return await stock_service.get_all_stocks(session=db)


@router.put("/{stock_id}", response_model=StockRead)
async def update_stock(stock_id: int, stock: StockUpdate, db: AsyncSession = Depends(get_db)) -> StockRead:
    db_stock = await stock_service.update_stock(session=db, stock_id=stock_id, stock_update=stock)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock


@router.delete("/{stock_id}", response_model=dict)
async def delete_stock(stock_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    success = await stock_service.delete_stock(session=db, stock_id=stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock not found")
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
    df = yf.download(req.ticker, start=req.start, end=req.end, auto_adjust=req.auto_adjust)
    if df is None or len(df) == 0:
        return {"saved": 0}
    saved = await stock_service.upsert_stocks_from_dataframe(
        session=db,
        df=df,
        ticker=req.ticker,
        name=req.name,
        market=req.market,
        currency=req.currency,
        auto_adjust=req.auto_adjust,
        timezone=req.timezone,
    )
    return {"saved": saved}


@router.post("/reset", response_model=dict)
async def reset_database() -> dict[str, bool]:
    await reset_db()
    return {"ok": True}
