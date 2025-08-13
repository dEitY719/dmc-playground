from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_session
from src.backend.models.stock import Stock
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
