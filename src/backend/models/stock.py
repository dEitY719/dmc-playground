from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel


class StockBase(SQLModel):
    """
    Base model for stock data, containing all common fields.
    """

    ticker: str = Field(index=True)
    name: Optional[str] = Field(default=None, index=True)
    market: Optional[str] = Field(default=None, index=True)
    currency: Optional[str] = Field(default="USD")
    time: datetime = Field(index=True)
    open: float
    high: float
    low: float
    close: float
    adjusted_close: Optional[float] = Field(default=None)
    volume: int


class Stock(StockBase, table=True):
    """
    Represents a stock's price and volume information at a specific time in the database.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )


class StockUpdate(SQLModel):
    """
    Model for updating a stock entry. All fields are optional.
    """

    name: Optional[str] = None
    market: Optional[str] = None
    currency: Optional[str] = None
    time: Optional[datetime] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    adjusted_close: Optional[float] = None
    volume: Optional[int] = None
