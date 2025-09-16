import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_create_stock(client: AsyncClient):
    """
    Test case for creating a new stock entry.
    """
    stock_data = {
        "ticker": "AAPL",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T10:00:00Z",
        "open": 150.0,
        "high": 152.5,
        "low": 149.5,
        "close": 152.0,
        "volume": 1000000,
    }
    response = await client.post("/stocks/", json=stock_data)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == stock_data["ticker"]
    assert data["open"] == stock_data["open"]
    assert "id" in data
    assert data["id"] is not None
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_read_stock(client: AsyncClient):
    """
    Test case for reading a single stock entry.
    """
    stock_data = {
        "ticker": "GOOGL",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T11:00:00Z",
        "open": 2800.0,
        "high": 2810.5,
        "low": 2795.0,
        "close": 2805.0,
        "volume": 500000,
    }
    create_response = await client.post("/stocks/", json=stock_data)
    assert create_response.status_code == 200
    created_stock = create_response.json()
    stock_id = created_stock["id"]

    response = await client.get(f"/stocks/{stock_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == stock_data["ticker"]
    assert data["id"] == stock_id


@pytest.mark.asyncio
async def test_read_all_stocks(client: AsyncClient):
    """
    Test case for reading all stock entries.
    """
    stock_data_1 = {
        "ticker": "MSFT",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T12:00:00Z",
        "open": 300.0,
        "high": 305.0,
        "low": 298.0,
        "close": 304.0,
        "volume": 700000,
    }
    stock_data_2 = {
        "ticker": "AMZN",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T13:00:00Z",
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 800000,
    }
    await client.post("/stocks/", json=stock_data_1)
    await client.post("/stocks/", json=stock_data_2)

    response = await client.get("/stocks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # There might be other stocks from previous tests if not properly cleaned
    tickers = [stock["ticker"] for stock in data]
    assert "MSFT" in tickers
    assert "AMZN" in tickers


@pytest.mark.asyncio
async def test_update_stock(client: AsyncClient):
    """
    Test case for updating an existing stock entry.
    """
    stock_data = {
        "ticker": "NVDA",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T14:00:00Z",
        "open": 500.0,
        "high": 510.0,
        "low": 498.0,
        "close": 508.0,
        "volume": 1200000,
    }
    create_response = await client.post("/stocks/", json=stock_data)
    assert create_response.status_code == 200
    created_stock = create_response.json()
    stock_id = created_stock["id"]

    updated_data = {"close": 512.5, "volume": 1300000}
    response = await client.put(f"/stocks/{stock_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["close"] == updated_data["close"]
    assert data["volume"] == updated_data["volume"]
    assert data["ticker"] == stock_data["ticker"]


@pytest.mark.asyncio
async def test_delete_stock(client: AsyncClient):
    """
    Test case for deleting an existing stock entry.
    """
    stock_data = {
        "ticker": "TSLA",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T15:00:00Z",
        "open": 800.0,
        "high": 810.0,
        "low": 795.0,
        "close": 805.0,
        "volume": 900000,
    }
    create_response = await client.post("/stocks/", json=stock_data)
    assert create_response.status_code == 200
    created_stock = create_response.json()
    stock_id = created_stock["id"]

    response = await client.delete(f"/stocks/{stock_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    get_response = await client.get(f"/stocks/{stock_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
@patch("yfinance.download")
async def test_download_and_store_endpoint(mock_yf_download: MagicMock, client: AsyncClient):
    import pandas as pd
    from datetime import datetime

    dates = pd.to_datetime(pd.date_range(start="2025-01-01", end="2025-01-03", freq="D"))
    df = pd.DataFrame(
        {
            "Open": [1.0, 2.0, 3.0],
            "High": [1.5, 2.5, 3.5],
            "Low": [0.5, 1.5, 2.5],
            "Close": [1.2, 2.2, 3.2],
            "Volume": [100, 200, 300],
        },
        index=dates,
    )
    mock_yf_download.return_value = df

    payload = {
        "ticker": "TEST",
        "start": "2025-01-01",
        "end": "2025-01-04",
        "auto_adjust": True,
        "timezone": "UTC",
        "name": "Test",
        "market": "TESTX",
        "currency": "USD"
    }

    resp = await client.post("/stocks/download", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("saved") == 3
