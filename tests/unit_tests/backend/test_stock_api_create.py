import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_stock(client: AsyncClient):
    """
    Test case for creating a new stock entry.
    """
    # 1. Define the data to be sent
    stock_data = {
        "ticker": "AAPL",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T10:00:00",
        "open": 150.0,
        "high": 152.5,
        "low": 149.5,
        "close": 152.0,
        "volume": 1000000,
    }

    # 2. Send a POST request to the endpoint
    response = await client.post("/robot/stocks/", json=stock_data)

    # 3. Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == stock_data["ticker"]
    assert data["open"] == stock_data["open"]
    assert "id" in data
    assert data["id"] is not None
