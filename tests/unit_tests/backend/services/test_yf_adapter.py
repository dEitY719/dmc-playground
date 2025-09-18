"""
Tests for the yfinance adapter service.
"""

import pandas as pd
import pytest

from src.backend.services.yf_adapter import df_to_stockbase


def test_df_to_stockbase_simple_dataframe():
    """
    Tests df_to_stockbase with a simple DataFrame having a DatetimeIndex.
    """
    dates = pd.to_datetime(pd.date_range(start="2025-01-01", end="2025-01-03", freq="D", tz="UTC"))
    # Set the index name to 'Date' to match what yfinance often provides
    dates.name = "Date"
    df = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
            "High": [110.0, 111.0, 112.0],
            "Low": [90.0, 91.0, 92.0],
            "Close": [105.0, 106.0, 107.0],
            "Volume": [1000, 2000, 3000],
        },
        index=dates,
    )

    records = df_to_stockbase(
        df, ticker="TEST", name="Test Co", market="TESTX", currency="USD", auto_adjust=True, timezone="UTC"
    )

    assert len(records) == 3
    assert records[0].ticker == "TEST"
    assert records[0].open == 100.0
    assert records[1].close == 106.0
    assert records[2].volume == 3000
    assert records[0].time.year == 2025
    assert records[0].time.month == 1
    assert records[0].time.day == 1

    # Test calculated fields (change, change_percent)
    assert pd.isna(records[0].change)  # First record has no previous close
    assert records[1].change == pytest.approx(1.0)  # 106.0 - 105.0
    assert records[1].change_percent == pytest.approx((1.0 / 105.0) * 100)


def test_df_to_stockbase_multiindex_dataframe():
    """
    Tests df_to_stockbase with a multi-index DataFrame, which can be returned by yfinance
    when downloading multiple tickers. The adapter should handle this gracefully.
    """
    # This test is more about ensuring the adapter doesn't crash on multi-index.
    # The service layer is responsible for iterating through tickers.
    dates = pd.to_datetime(pd.date_range(start="2025-01-01", end="2025-01-02", freq="D", tz="UTC"))
    dates.name = "Date"
    df = pd.DataFrame(
        {
            ("TEST1", "Open"): [100, 102],
            ("TEST1", "Close"): [101, 103],
            ("TEST1", "Volume"): [1000, 1100],
            ("TEST2", "Open"): [200, 202],
            ("TEST2", "Close"): [201, 203],
            ("TEST2", "Volume"): [2000, 2100],
        },
        index=dates,
    )
    # Reorder columns to be more realistic (Open, Close, Volume per ticker)
    df.columns = pd.MultiIndex.from_tuples(df.columns)

    # The adapter is designed to work with a single ticker's DataFrame.
    # We simulate this by selecting one ticker's data.
    df_single = df["TEST1"].copy()
    # yfinance multi-index download doesn't include High/Low, so we add them for the test
    df_single["High"] = [105, 107]
    df_single["Low"] = [95, 97]

    records = df_to_stockbase(
        df_single, ticker="TEST1", name="Test1 Co", market="TESTX", currency="USD", auto_adjust=False, timezone="UTC"
    )

    assert len(records) == 2
    assert records[0].ticker == "TEST1"
    assert records[0].open == 100
    assert records[1].close == 103


def test_df_to_stockbase_with_adj_close():
    """
    Tests that 'Adj Close' is correctly picked up when auto_adjust is False.
    """
    dates = pd.to_datetime(pd.date_range(start="2025-01-01", end="2025-01-02", freq="D", tz="UTC"))
    dates.name = "Date"
    df = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [110.0, 111.0],
            "Low": [90.0, 91.0],
            "Close": [105.0, 106.0],
            "Adj Close": [104.5, 105.5],
            "Volume": [1000, 2000],
        },
        index=dates,
    )

    records = df_to_stockbase(
        df, ticker="ADJTEST", name="Adj Co", market="TESTX", currency="USD", auto_adjust=False, timezone="UTC"
    )

    assert len(records) == 2
    assert records[0].adjusted_close == 104.5
    assert records[1].adjusted_close == 105.5


def test_df_to_stockbase_empty_dataframe():
    """
    Tests that an empty DataFrame results in an empty list of records.
    """
    df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
    df.index.name = "Date"

    records = df_to_stockbase(
        df, ticker="EMPTY", name="Empty Co", market="TESTX", currency="USD", auto_adjust=True, timezone="UTC"
    )

    assert len(records) == 0
