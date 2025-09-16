# tests/unit_tests/backend/services/test_stock_downloader.py
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.backend.services.stock_downloader import StockDownloader


@pytest.fixture
def tmp_metadata_file(tmp_path: Path) -> Path:
    """테스트용 임시 메타데이터 파일을 생성하는 pytest fixture."""
    return tmp_path / "test_metadata.json"


def create_mock_data(start_date: str, end_date: str) -> pd.DataFrame:
    """지정된 기간 동안의 모의 주식 데이터 DataFrame을 생성합니다."""
    dates = pd.to_datetime(pd.date_range(start=start_date, end=end_date, freq="D"))
    data = {
        "Open": [100] * len(dates),
        "High": [105] * len(dates),
        "Low": [95] * len(dates),
        "Close": [102] * len(dates),
        "Volume": [10000] * len(dates),
    }
    return pd.DataFrame(data, index=dates)


@patch("yfinance.download")
def test_download_scenarios(mock_yf_download: MagicMock, tmp_metadata_file: Path):
    """
    StockDownloader의 다운로드 시나리오를 테스트합니다.

    - 시나리오 1: 처음으로 데이터를 다운로드합니다.
    - 시나리오 2: 이전에 받은 데이터 이후의 새로운 데이터만 다운로드합니다.
    """
    downloader = StockDownloader(metadata_path=str(tmp_metadata_file))

    # --- 시나리오 1: 2025-08-15에 데이터 다운로드 ---
    # 모의 데이터 설정
    mock_data_soxl_1 = create_mock_data("2025-01-01", "2025-08-14")
    mock_data_aapl_1 = create_mock_data("2025-01-01", "2025-07-14")

    # yf.download가 호출될 때 반환할 값을 설정
    mock_yf_download.side_effect = [mock_data_soxl_1, mock_data_aapl_1]

    # SOXL 데이터 다운로드
    soxl_data_1 = downloader.download("SOXL", start_date="2025-01-01", end_date="2025-08-15")
    # AAPL 데이터 다운로드
    aapl_data_1 = downloader.download("AAPL", start_date="2025-01-01", end_date="2025-07-15")

    # 다운로드된 데이터 검증
    assert soxl_data_1 is not None
    assert soxl_data_1.index.min() == pd.to_datetime("2025-01-01")
    assert soxl_data_1.index.max() == pd.to_datetime("2025-08-14")
    assert aapl_data_1 is not None
    assert aapl_data_1.index.max() == pd.to_datetime("2025-07-14")

    # yf.download 호출 인수 검증
    mock_yf_download.assert_any_call("SOXL", start="2025-01-01", end="2025-08-16", auto_adjust=True)
    mock_yf_download.assert_any_call("AAPL", start="2025-01-01", end="2025-07-16", auto_adjust=True)

    # 메타데이터 검증
    assert downloader.ticker_metadata["SOXL"] == "2025-08-14"
    assert downloader.ticker_metadata["AAPL"] == "2025-07-14"
    with open(tmp_metadata_file, encoding="utf-8") as f:
        metadata = json.load(f)
    assert metadata["SOXL"] == "2025-08-14"

    # --- 시나리오 2: 2025-08-23에 다시 데이터 다운로드 ---
    # 모의 데이터 설정
    mock_data_soxl_2 = create_mock_data("2025-08-15", "2025-08-22")
    mock_data_aapl_2 = create_mock_data("2025-07-15", "2025-08-22")
    mock_yf_download.side_effect = [mock_data_soxl_2, mock_data_aapl_2]

    # SOXL, AAPL 데이터 다시 다운로드
    soxl_data_2 = downloader.download("SOXL", start_date="2025-01-01", end_date="2025-08-23")
    aapl_data_2 = downloader.download("AAPL", start_date="2025-01-01", end_date="2025-08-23")

    # 다운로드된 데이터 검증 (새로운 데이터만 있어야 함)
    assert soxl_data_2 is not None
    assert soxl_data_2.index.min() == pd.to_datetime("2025-08-15")
    assert soxl_data_2.index.max() == pd.to_datetime("2025-08-22")
    assert aapl_data_2 is not None
    assert aapl_data_2.index.min() == pd.to_datetime("2025-07-15")

    # yf.download 호출 인수 검증 (시작 날짜가 업데이트되었는지 확인)
    mock_yf_download.assert_any_call("SOXL", start="2025-08-15", end="2025-08-24", auto_adjust=True)
    mock_yf_download.assert_any_call("AAPL", start="2025-07-15", end="2025-08-24", auto_adjust=True)

    # 메타데이터 검증
    assert downloader.ticker_metadata["SOXL"] == "2025-08-22"
    assert downloader.ticker_metadata["AAPL"] == "2025-08-22"
    with open(tmp_metadata_file, encoding="utf-8") as f:
        metadata = json.load(f)
    assert metadata["SOXL"] == "2025-08-22"
