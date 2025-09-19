"""
Stock transaction models for database and API communication.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .stock import StockInfo


class StockTransactionBase(SQLModel):
    """
    Base model for stock transaction data.
    """

    user_id: int = Field(index=True)
    transaction_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, index=True))
    brokerage: str = Field(max_length=50, index=True)
    transaction_type: str = Field(max_length=10)  # e.g., "매수", "매도"
    ticker: str = Field(index=True)
    transaction_price: float
    quantity: int
    total_amount: float


class StockTransaction(StockTransactionBase, table=True):
    """
    Database model for stock transaction data.
    """

    __tablename__ = "stocktransaction"

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

    stock_info: "StockInfo" = Relationship(back_populates="transactions")


class StockTransactionCreate(StockTransactionBase):
    """
    Model for creating a new stock transaction entry.
    """

    stock_info_id: int


class StockTransactionRead(StockTransactionBase):
    """
    Model for reading stock transaction data from the API.
    """

    id: int
    stock_info_id: int
    created_at: datetime
    updated_at: datetime


class StockTransactionUpdate(SQLModel):
    """
    Model for updating a stock transaction entry.
    """

    brokerage: str | None = None
    transaction_type: str | None = None
    transaction_price: float | None = None
    quantity: int | None = None
    total_amount: float | None = None
