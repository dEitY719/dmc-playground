from datetime import datetime, timezone

from sqlmodel import Column, DateTime, Field, SQLModel


class StockBase(SQLModel):
    """
    Base model for stock data, containing all common fields.
    """

    ticker: str = Field(index=True)
    name: str | None = Field(default=None, index=True)
    market: str | None = Field(default=None, index=True)
    currency: str | None = Field(default="USD")
    time: datetime = Field(index=True)
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None = Field(default=None)
    volume: int


class Stock(StockBase, table=True):
    """
    Represents a stock's price and volume information at a specific time in the database.
    """

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
