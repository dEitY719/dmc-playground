import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_stock(client: AsyncClient):
    """
    Test case for reading a single stock entry.
    """
    # 1. Create a stock to read
    stock_data = {
        "ticker": "GOOGL",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T11:00:00",
        "open": 2800.0,
        "high": 2810.5,
        "low": 2795.0,
        "close": 2805.0,
        "volume": 500000,
    }
    create_response = await client.post("/robot/stocks/", json=stock_data)
    assert create_response.status_code == 200
    created_stock = create_response.json()
    stock_id = created_stock["id"]

    # 2. Send a GET request to the endpoint
    response = await client.get(f"/robot/stocks/{stock_id}")

    # 3. Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == stock_data["ticker"]
    assert data["id"] == stock_id
