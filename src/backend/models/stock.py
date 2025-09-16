from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Column, DateTime, Field, SQLModel


class StockBase(SQLModel):
    """
    Base model for stock data, containing all common fields.
    """

    ticker: str = Field(index=True)
    name: str | None = Field(default=None, index=True)
    market: str | None = Field(default=None, index=True)
    currency: str | None = Field(default="USD")
    time: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, index=True))
    open: float
    high: float
    low: float
    close: float
    previous_close: float | None = Field(default=None)
    change: float | None = Field(default=None)
    change_percent: float | None = Field(default=None)
    adjusted_close: float | None = Field(default=None)
    volume: int


class StockCreate(StockBase):
    """
    Model for creating a new stock entry.
    """

    pass


class StockRead(StockBase):
    """
    Model for reading stock data from the API.
    """

    id: int
    created_at: datetime
    updated_at: datetime


class Stock(StockBase, table=True):
    """
    Represents a stock's price and volume information at a specific time in the database.
    """

    __table_args__ = (UniqueConstraint("ticker", "time", name="uq_stock_ticker_time"),)

    id: int | None = Field(default=None, primary_key=True)
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

    name: str | None = None
    market: str | None = None
    currency: str | None = None
    time: datetime | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    adjusted_close: float | None = None
    volume: int | None = None
