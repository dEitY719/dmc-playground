"""
Stock holding detail models for database and API communication.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .stock import StockInfo


class StockHoldingDetailBase(SQLModel):
    """
    Base model for stock holding detail data.
    """

    user_id: int = Field(index=True)
    ticker: str = Field(index=True)
    holding_quantity: int = Field(default=0)
    average_buy_price: float = Field(default=0.0)
    total_buy_amount: float = Field(default=0.0)
    current_price: float | None = Field(default=None)
    total_evaluation_amount: float | None = Field(default=None)
    total_profit: float | None = Field(default=None)
    krw_profit: float | None = Field(default=None)
    daily_profit: float | None = Field(default=None)
    current_exchange_rate: float | None = Field(default=None)


class StockHoldingDetail(StockHoldingDetailBase, table=True):
    """
    Database model for stock holding detail data.
    """

    __tablename__ = "stockholdingdetail"
    __table_args__ = (UniqueConstraint("user_id", "stock_info_id", name="uq_user_stock_holding"),)

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

    stock_info: "StockInfo" = Relationship(back_populates="holding_details")


class StockHoldingDetailCreate(StockHoldingDetailBase):
    """
    Model for creating a new stock holding detail entry.
    """

    stock_info_id: int


class StockHoldingDetailRead(StockHoldingDetailBase):
    """
    Model for reading stock holding detail data from the API.
    """

    id: int
    stock_info_id: int
    created_at: datetime
    updated_at: datetime


class StockHoldingDetailUpdate(SQLModel):
    """
    Model for updating a stock holding detail entry.
    """

    holding_quantity: int | None = None
    average_buy_price: float | None = None
    total_buy_amount: float | None = None
    current_price: float | None = None
    total_evaluation_amount: float | None = None
    total_profit: float | None = None
    krw_profit: float | None = None
    daily_profit: float | None = None
    current_exchange_rate: float | None = None
