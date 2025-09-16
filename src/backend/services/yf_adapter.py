from __future__ import annotations

import pandas as pd

from src.backend.models.stock import StockBase


def df_to_stockbase(
    df: pd.DataFrame,
    ticker: str,
    name: str | None = None,
    market: str | None = None,
    currency: str = "USD",
    auto_adjust: bool = True,
    timezone: str = "UTC",
) -> list[StockBase]:
    """
    yfinance.download() DataFrame을 StockBase 객체 리스트로 변환

    Args:
        df (pd.DataFrame): yfinance.download 결과
        ticker (str): 종목 코드
        name (str | None): 종목 이름
        market (str | None): 거래 시장 (예: KOSPI, NASDAQ)
        currency (str): 통화 단위 (기본: USD)
        auto_adjust (bool): yfinance auto_adjust 설정과 일치시켜 adjusted_close 처리
        timezone (str): 결과 인덱스의 타임존. naive면 tz_localize, aware면 tz_convert

    Returns:
        List[StockBase]: 변환된 StockBase 객체 리스트
    """

    # yfinance 컬럼명을 StockBase 기준으로 변환
    column_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }

    # MultiIndex(Price, Ticker) 구조일 경우 단일 티커 슬라이스
    if isinstance(df.columns, pd.MultiIndex):
        if "Ticker" in df.columns.names:
            try:
                df = df.xs(ticker, level="Ticker", axis=1)
            except Exception:
                # 예상치 못한 구조면 그대로 진행 (rename에서 필요한 컬럼만 사용)
                pass

    # 타임존 정규화
    if isinstance(df.index, pd.DatetimeIndex):
        if df.index.tz is None:
            df.index = df.index.tz_localize(timezone)
        else:
            df.index = df.index.tz_convert(timezone)

    df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

    records: list[StockBase] = []
    previous_close: float | None = None

    for idx, row in df.iterrows():
        # adjusted_close 컬럼이 있으면 우선 사용 (auto_adjust=False 시나리오)
        adjusted_close_val = None
        if not auto_adjust and "Adj Close" in df.columns:
            try:
                adjusted_close_val = float(row["Adj Close"]) if pd.notna(row["Adj Close"]) else None
            except Exception:
                adjusted_close_val = None
        # 결측값 방어적 처리
        open_val = float(row["open"]) if "open" in row and pd.notna(row["open"]) else None
        high_val = float(row["high"]) if "high" in row and pd.notna(row["high"]) else None
        low_val = float(row["low"]) if "low" in row and pd.notna(row["low"]) else None
        close_val = float(row["close"]) if "close" in row and pd.notna(row["close"]) else None
        # yfinance는 volume이 float로 올 수 있으니 안전 캐스팅
        volume_val = 0
        if "volume" in row and pd.notna(row["volume"]):
            try:
                volume_val = int(float(row["volume"]))
            except Exception:
                volume_val = 0

        change = None
        change_percent = None
        if previous_close is not None and close_val is not None:
            change = close_val - previous_close
            if previous_close != 0:
                change_percent = (change / previous_close) * 100

        record = StockBase(
            ticker=ticker,
            name=name,
            market=market,
            currency=currency,
            time=idx.to_pydatetime() if isinstance(idx, pd.Timestamp) else idx,
            open=open_val,
            high=high_val,
            low=low_val,
            close=close_val,
            previous_close=previous_close,
            change=change,
            change_percent=change_percent,
            adjusted_close=(close_val if auto_adjust else adjusted_close_val),
            volume=volume_val,
        )

        records.append(record)
        previous_close = close_val if close_val is not None else previous_close

    return records
