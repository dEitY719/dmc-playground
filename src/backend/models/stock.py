"""
Stock models for database and API communication.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


# -----------------
# StockInfo Models
# -----------------
class StockInfoBase(SQLModel):
    """
    Base model for stock metadata.
    """

    ticker: str = Field(unique=True, index=True)
    name: str | None = Field(default=None, index=True)
    market: str | None = Field(default=None, index=True)
    currency: str | None = Field(default="USD")


class StockInfo(StockInfoBase, table=True):
    """
    Database model for stock metadata.
    """

    __tablename__ = "stockinfo"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    prices: list["StockPrice"] = Relationship(back_populates="stock_info")


class StockInfoCreate(StockInfoBase):
    """
    Model for creating a new stock info entry.
    """

    pass


class StockInfoUpdate(SQLModel):
    """
    Model for updating a stock info entry.
    """

    name: str | None = None
    market: str | None = None
    currency: str | None = None


class StockInfoRead(StockInfoBase):
    """
    Model for reading stock info from the API.
    """

    id: int
    created_at: datetime
    updated_at: datetime


# -----------------
# StockPrice Models
# -----------------
class StockPriceBase(SQLModel):
    """
    Base model for stock price data.
    """

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


class StockPrice(StockPriceBase, table=True):
    """
    Database model for stock price data.
    """

    __tablename__ = "stockprice"
    __table_args__ = (UniqueConstraint("stock_info_id", "time", name="uq_stock_price_stock_info_id_time"),)

    id: int | None = Field(default=None, primary_key=True)
    stock_info_id: int = Field(foreign_key="stockinfo.id", index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    stock_info: StockInfo = Relationship(back_populates="prices")


class StockPriceCreate(StockPriceBase):
    """
    Model for creating a new stock price entry.
    """

    stock_info_id: int


class StockPriceRead(StockPriceBase):
    """
    Model for reading stock price data from the API.
    """

    id: int
    stock_info_id: int
    created_at: datetime
    updated_at: datetime


# -----------------
# Combined Read Models for API
# -----------------
class StockInfoReadWithPrices(StockInfoRead):
    """
    Model for reading stock info along with its associated prices.
    """

    prices: list[StockPriceRead] = []
