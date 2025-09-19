"""
Stock price models for database and API communication.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .stock import StockInfo


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

    stock_info: "StockInfo" = Relationship(back_populates="prices")


class StockPriceCreate(StockPriceBase):
    """
    Model for creating a new stock price entry.
    """

    stock_info_id: int


class StockPriceRead(StockPriceBase):
    """
    Model for reading stock price data from the API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_info_id: int
    created_at: datetime
    updated_at: datetime
