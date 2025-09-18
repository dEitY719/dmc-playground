"""
Adapter for converting yfinance data to the application's data models.
"""

import numpy as np
import pandas as pd
import pytz

from src.backend.models.stock import StockInfoBase, StockPriceBase


class StockData(StockInfoBase, StockPriceBase):
    """
    A temporary combined model for processing data from yfinance.
    """

    pass


def df_to_stockbase(
    df: pd.DataFrame,
    ticker: str,
    name: str | None,
    market: str | None,
    currency: str,
    auto_adjust: bool,
    timezone: str,
) -> list[StockData]:
    """
    Converts a yfinance DataFrame into a list of StockData objects.
    """
    if df.empty:
        return []

    records = []
    df_reset = df.reset_index()

    # 'Date' or 'Datetime' column to timezone-aware datetime objects
    date_col = next((col for col in df_reset.columns if col in ["Date", "Datetime"]), None)
    if not date_col:
        raise ValueError("DataFrame must have a 'Date' or 'Datetime' column.")

    df_reset[date_col] = pd.to_datetime(df_reset[date_col])
    if df_reset[date_col].dt.tz is None:
        df_reset[date_col] = df_reset[date_col].dt.tz_localize(pytz.utc).dt.tz_convert(timezone)
    else:
        df_reset[date_col] = df_reset[date_col].dt.tz_convert(timezone)

    # Calculate previous_close, change, and change_percent
    df_reset["previous_close"] = df_reset["Close"].shift(1)
    df_reset["change"] = df_reset["Close"] - df_reset["previous_close"]
    df_reset["change_percent"] = (df_reset["change"] / df_reset["previous_close"]) * 100

    # Replace NaN values with None for JSON compatibility
    df_processed = df_reset.replace({np.nan: None})

    for _, row in df_processed.iterrows():
        record_data = {
            "ticker": ticker,
            "name": name,
            "market": market,
            "currency": currency,
            "time": row[date_col],
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"],
            "previous_close": row["previous_close"],
            "change": row["change"],
            "change_percent": row["change_percent"],
            "adjusted_close": row.get("Adj Close") if not auto_adjust else None,
        }
        records.append(StockData(**record_data))
    return records
