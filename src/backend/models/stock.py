from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from src.backend.models.holding import StockHoldingDetail
from src.backend.models.price import StockPrice, StockPriceRead
from src.backend.models.transaction import StockTransaction

if TYPE_CHECKING:
    pass


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
    transactions: list["StockTransaction"] = Relationship(back_populates="stock_info")
    holding_details: list["StockHoldingDetail"] = Relationship(back_populates="stock_info")


class StockInfoCreate(StockInfoBase):
    """
    Model for creating a new stock info entry.
    """


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
# Combined Read Models for API
# -----------------
class StockInfoReadWithPrices(StockInfoRead):
    """
    Model for reading stock info along with its associated prices.
    """

    model_config = ConfigDict(from_attributes=True)

    prices: list["StockPriceRead"] = []


StockInfoReadWithPrices.model_rebuild()
