# src/backend/services/stock_downloader.py
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf


class StockDownloader:
    """
    yfinance를 사용하여 주식 데이터를 효율적으로 다운로드하고 관리하는 클래스.

    - 각 Ticker별로 마지막으로 다운로드한 날짜를 메타데이터로 관리하여 중복 다운로드를 방지합니다.
    - 다운로드한 데이터는 DataFrame으로 반환하며, 데이터베이스 저장을 위한 준비를 합니다.
    """

    def __init__(self, metadata_path: str = "stock_metadata.json"):
        """
        StockDownloader를 초기화합니다.

        Args:
            metadata_path (str): Ticker별 다운로드 메타데이터를 저장할 JSON 파일 경로.
        """
        self.metadata_path = Path(metadata_path)
        self.ticker_metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, str]:
        """메타데이터 파일에서 Ticker별 마지막 다운로드 날짜를 로드합니다."""
        if self.metadata_path.exists():
            with open(self.metadata_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """현재 Ticker 메타데이터를 파일에 저장합니다."""
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.ticker_metadata, f, indent=4)

    def download(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        auto_adjust: bool = True,
    ) -> pd.DataFrame | None:
        """
        지정된 Ticker의 주식 데이터를 다운로드합니다.

        메타데이터를 확인하여 필요한 경우에만 데이터를 다운로드합니다.

        Args:
            ticker (str): 다운로드할 주식 Ticker (예: "SOXL", "AAPL").
            start_date (str): 데이터를 다운로드할 시작 날짜 (YYYY-MM-DD).
            end_date (str): 데이터를 다운로드할 종료 날짜 (YYYY-MM-DD).
            auto_adjust (bool): yfinance의 auto_adjust 옵션.

        Returns:
            pd.DataFrame | None: 다운로드한 주식 데이터. 새로운 데이터가 없으면 None을 반환합니다.
        """
        effective_start_date = self._get_effective_start_date(ticker, start_date)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        if effective_start_date > end_dt:
            print(f"[{ticker}] No new data to download. Already up-to-date.")
            return None

        print(f"[{ticker}] Downloading data from {effective_start_date.strftime('%Y-%m-%d')} to {end_date}")

        # yfinance는 end_date를 포함하지 않으므로 하루를 더해줍니다.
        download_end_date = (end_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        data = yf.download(
            ticker,
            start=effective_start_date.strftime("%Y-%m-%d"),
            end=download_end_date,
            auto_adjust=auto_adjust,
        )

        if data.empty:
            print(f"[{ticker}] No data found for the given period.")
            return None

        # Convert timezone-aware index to a specific timezone
        if data.index.tz is not None:
            data.index = data.index.tz_convert("UTC")
        else:
            data.index = data.index.tz_localize("UTC")

        # 다운로드 성공 시 메타데이터 업데이트
        last_date_in_data = data.index[-1].strftime("%Y-%m-%d")
        self.ticker_metadata[ticker] = last_date_in_data
        self._save_metadata()
        print(f"[{ticker}] Download complete. Last date updated to {last_date_in_data}.")

        return data

    def _get_effective_start_date(self, ticker: str, requested_start_date: str) -> date:
        """
        메타데이터를 기반으로 실제 다운로드를 시작할 날짜를 결정합니다.

        Args:
            ticker (str): 확인할 Ticker.
            requested_start_date (str): 사용자가 요청한 시작 날짜.

        Returns:
            datetime.date: 실제 다운로드를 시작해야 하는 날짜.
        """
        if ticker in self.ticker_metadata:
            last_download_date_str = self.ticker_metadata[ticker]
            last_download_date = datetime.strptime(last_download_date_str, "%Y-%m-%d").date()
            # 마지막으로 받은 날짜의 다음 날부터 다운로드 시작
            return last_download_date + timedelta(days=1)

        return datetime.strptime(requested_start_date, "%Y-%m-%d").date()
