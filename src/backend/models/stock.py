from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Stock(SQLModel, table=True):
    """
    Represents a stock's price and volume information at a specific time.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    market: Optional[str] = Field(default=None, index=True)
    currency: Optional[str] = Field(default="USD")

    time: datetime = Field(index=True)
    open: float
    high: float
    low: float
    close: float
    volume: int

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
