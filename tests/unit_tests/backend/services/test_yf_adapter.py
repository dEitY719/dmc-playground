import pandas as pd

from src.backend.services.yf_adapter import df_to_stockbase


def test_df_to_stockbase_simple_dataframe():
    dates = pd.to_datetime(pd.date_range(start="2025-01-01", end="2025-01-03", freq="D"))
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
    assert records[0].close == 105.0
    assert records[0].previous_close is None
    assert records[1].previous_close == 105.0
    assert round(records[1].change or 0.0, 6) == 1.0
    assert round(records[1].change_percent or 0.0, 6) == round((1.0 / 105.0) * 100, 6)
    assert records[0].adjusted_close == 105.0  # auto_adjust=True -> adjusted_close=close


def test_df_to_stockbase_multiindex_dataframe():
    dates = pd.to_datetime(pd.date_range(start="2025-02-01", end="2025-02-02", freq="D"))
    data = {
        ("Open", "AAA"): [10.0, 11.0],
        ("High", "AAA"): [12.0, 13.0],
        ("Low", "AAA"): [9.0, 10.0],
        ("Close", "AAA"): [11.0, 12.0],
        ("Volume", "AAA"): [100, 200],
        ("Open", "BBB"): [20.0, 21.0],
        ("High", "BBB"): [22.0, 23.0],
        ("Low", "BBB"): [19.0, 20.0],
        ("Close", "BBB"): [21.0, 22.0],
        ("Volume", "BBB"): [300, 400],
    }
    df = pd.DataFrame(data, index=dates)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["Price", "Ticker"])

    records = df_to_stockbase(
        df, ticker="AAA", name=None, market=None, currency="USD", auto_adjust=True, timezone="UTC"
    )

    assert len(records) == 2
    assert records[0].open == 10.0
    assert records[0].close == 11.0
    assert records[0].volume == 100
