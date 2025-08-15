import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_stock(client: AsyncClient):
    """
    Test case for updating an existing stock entry.
    """
    # 1. Create a stock to update
    stock_data = {
        "ticker": "MSFT",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T12:00:00",
        "open": 300.0,
        "high": 305.0,
        "low": 298.0,
        "close": 304.0,
        "volume": 700000,
    }
    create_response = await client.post("/stocks/", json=stock_data)
    assert create_response.status_code == 200
    created_stock = create_response.json()
    stock_id = created_stock["id"]

    # 2. Define the updated data
    updated_data = {"close": 306.5, "volume": 750000}

    # 3. Send a PUT request to the endpoint
    response = await client.put(f"/stocks/{stock_id}", json=updated_data)

    # 4. Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["close"] == updated_data["close"]
    assert data["volume"] == updated_data["volume"]
    assert data["ticker"] == stock_data["ticker"]  # Ticker should not change
