"""
Tests for the stock API CRUD operations.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from httpx import AsyncClient


@pytest.fixture
def mock_yf_download_fixture():
    """
    Provides a fixture for mocking yfinance.download.
    This mock now uses a side_effect to return data based on the requested date range,
    ensuring timezone-awareness and end-date exclusivity are handled correctly.
    """

    def yf_download_side_effect(*args, **kwargs):
        # Ensure start and end dates are timezone-aware to match the DataFrame index
        start_date = pd.to_datetime(kwargs.get("start", "2025-01-01"), utc=True)
        # yfinance download is exclusive of the end date, so we subtract one day for slicing
        end_date = pd.to_datetime(kwargs.get("end", "2025-01-04"), utc=True) - pd.Timedelta(days=1)

        all_dates = pd.to_datetime(pd.date_range(start="2025-01-01", end="2025-01-03", freq="D", tz="UTC"))
        all_dates.name = "Date"
        full_df = pd.DataFrame(
            {
                "Open": [1.0, 2.0, 3.0],
                "High": [1.5, 2.5, 3.5],
                "Low": [0.5, 1.5, 2.5],
                "Close": [1.2, 2.2, 3.2],
                "Volume": [100, 200, 300],
            },
            index=all_dates,
        )
        # Filter the DataFrame based on the requested start and end dates
        return full_df.loc[start_date:end_date]

    with patch("yfinance.download", side_effect=yf_download_side_effect) as mock:
        yield mock


@pytest.mark.asyncio
async def test_download_and_store(client: AsyncClient, mock_yf_download_fixture: MagicMock):
    """
    Test downloading data, storing it, and verifying the upsert logic.
    """
    ticker = "TEST"
    payload = {
        "ticker": ticker,
        "start": "2025-01-01",
        "end": "2025-01-04",  # yfinance is exclusive of the end date
        "name": "Test Company",
        "market": "TESTX",
    }

    # 1. First download, should save 3 new records (Jan 1, 2, 3)
    response = await client.post("/stock/download", json=payload)
    assert response.status_code == 200
    assert response.json() == {"saved": 3}

    # 2. Verify the data was saved correctly
    response = await client.get(f"/stock/info/ticker/{ticker}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == ticker
    assert data["name"] == "Test Company"
    assert len(data["prices"]) == 3
    assert data["prices"][0]["open"] == 1.0
    assert data["prices"][1]["close"] == 2.2
    assert data["prices"][2]["volume"] == 300

    # 3. Second download for the same period, should save 0 new records
    response = await client.post("/stock/download", json=payload)
    assert response.status_code == 200
    assert response.json() == {"saved": 0}


@pytest.mark.asyncio
async def test_read_stock_info_by_id(client: AsyncClient, mock_yf_download_fixture: MagicMock):
    """
    Test reading stock info by its database ID.
    """
    ticker = "READBYID"
    # Request data only for Jan 1 and Jan 2 (end="2025-01-03" is exclusive)
    payload = {"ticker": ticker, "start": "2025-01-01", "end": "2025-01-03"}
    await client.post("/stock/download", json=payload)

    # Get the created stock info to find its ID
    response = await client.get(f"/stock/info/ticker/{ticker}")
    assert response.status_code == 200
    stock_info_id = response.json()["id"]

    # Read by ID
    response = await client.get(f"/stock/info/id/{stock_info_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == stock_info_id
    assert data["ticker"] == ticker
    assert len(data["prices"]) == 2


@pytest.mark.asyncio
async def test_read_all_stock_infos(client: AsyncClient, mock_yf_download_fixture: MagicMock):
    """
    Test reading all stock infos (without prices).
    """
    # Create two stock info entries
    await client.post("/stock/download", json={"ticker": "ALL1", "start": "2025-01-01", "end": "2025-01-02"})
    await client.post("/stock/download", json={"ticker": "ALL2", "start": "2025-01-01", "end": "2025-01-02"})

    response = await client.get("/stock/info/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    tickers = {item["ticker"] for item in data}
    assert "ALL1" in tickers
    assert "ALL2" in tickers
    assert "prices" not in data[0]


@pytest.mark.asyncio
async def test_update_stock_info(client: AsyncClient, mock_yf_download_fixture: MagicMock):
    """
    Test updating a stock's metadata.
    """
    ticker = "UPDATE"
    payload = {"ticker": ticker, "start": "2025-01-01", "end": "2025-01-02", "name": "Old Name"}
    await client.post("/stock/download", json=payload)

    # Get ID
    response = await client.get(f"/stock/info/ticker/{ticker}")
    stock_info_id = response.json()["id"]

    # Update
    update_payload = {"name": "New Name", "market": "NEW_MARKET"}
    response = await client.put(f"/stock/info/{stock_info_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["market"] == "NEW_MARKET"
    assert data["ticker"] == ticker


@pytest.mark.asyncio
async def test_delete_stock_info(client: AsyncClient, mock_yf_download_fixture: MagicMock):
    """
    Test deleting a stock and its associated prices.
    """
    ticker = "DELETE"
    payload = {"ticker": ticker, "start": "2025-01-01", "end": "2025-01-02"}
    await client.post("/stock/download", json=payload)

    # Get ID
    response = await client.get(f"/stock/info/ticker/{ticker}")
    stock_info_id = response.json()["id"]

    # Delete
    response = await client.delete(f"/stock/info/{stock_info_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Verify deletion
    response = await client.get(f"/stock/info/id/{stock_info_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_nonexistent_stock(client: AsyncClient):
    """
    Test reading non-existent stock info returns 404.
    """
    response = await client.get("/stock/info/id/999999")
    assert response.status_code == 404

    response = await client.get("/stock/info/ticker/NONEXISTENT")
    assert response.status_code == 404
