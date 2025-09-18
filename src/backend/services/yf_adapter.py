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
    Handles both single-level and MultiIndex DataFrames.
    """
    if df.empty:
        return []

    # --- Step 1: Reset index ---
    df_reset = df.reset_index(names=["Datetime"])

    # --- Step 2: Handle MultiIndex columns ---
    if isinstance(df_reset.columns, pd.MultiIndex):
        # yfinance 경우 (field, ticker) 또는 (ticker, field) 구조가 있음
        level0, level1 = df_reset.columns.levels[0], df_reset.columns.levels[1]

        if "Close" in level0 or "Adj Close" in level0:
            # (field, ticker) 구조
            field_first = True
        else:
            # (ticker, field) 구조
            field_first = False

        def pick(colname: str) -> pd.Series | None:
            if field_first:
                if (colname, ticker) in df_reset.columns:
                    return df_reset[(colname, ticker)]
            else:
                if (ticker, colname) in df_reset.columns:
                    return df_reset[(ticker, colname)]
            return None

        # 기본 컬럼 뽑기
        open_ = pick("Open")
        high = pick("High")
        low = pick("Low")
        close = pick("Adj Close") if pick("Adj Close") is not None else pick("Close")
        volume = pick("Volume")

        # 새로운 단일 레벨 DF 구성
        df_reset = pd.DataFrame(
            {
                "Datetime": df_reset["Datetime"],
                "Open": open_,
                "High": high,
                "Low": low,
                "Close": close,
                "Volume": volume,
            }
        )

    # --- Step 3: Datetime 처리 (타임존 정규화) ---
    date_col = "Datetime"
    df_reset[date_col] = pd.to_datetime(df_reset[date_col])
    if df_reset[date_col].dt.tz is None:
        df_reset[date_col] = df_reset[date_col].dt.tz_localize(pytz.utc).dt.tz_convert(timezone)
    else:
        df_reset[date_col] = df_reset[date_col].dt.tz_convert(timezone)

    # --- Step 4: change, change_percent 계산 ---
    df_reset["previous_close"] = df_reset["Close"].shift(1)
    df_reset["change"] = df_reset["Close"] - df_reset["previous_close"]
    df_reset["change_percent"] = (df_reset["change"] / df_reset["previous_close"]) * 100

    # --- Step 5: NaN → None 변환 ---
    df_processed = df_reset.replace({np.nan: None})

    # --- Step 6: StockData 변환 ---
    records = []
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
