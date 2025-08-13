from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Stock(SQLModel, table=True):
    """
    Represents a stock's price and volume information at a specific time.

    Attributes:
        id (Optional[int]): The unique identifier for the stock entry.
        ticker (str): The stock ticker symbol (e.g., "AAPL").
        name (Optional[str]): The full name of the company.
        market (Optional[str]): The market where the stock is traded (e.g., "NASDAQ").
        currency (Optional[str]): The currency in which the stock is traded (e.g., "USD").
        time (datetime): The timestamp of the stock data.
        open (float): The opening price of the stock.
        high (float): The highest price of the stock during the period.
        low (float): The lowest price of the stock during the period.
        close (float): The closing price of the stock.
        adjusted_close (Optional[float]): The adjusted closing price, accounting for splits and dividends.
        volume (int): The trading volume of the stock.
        created_at (datetime): The timestamp when the record was created.
        updated_at (datetime): The timestamp when the record was last updated.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
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

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
