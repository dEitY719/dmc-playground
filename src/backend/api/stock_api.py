from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
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
    return db_stock


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
