import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_stock(client: AsyncClient):
    """
    Test case for deleting an existing stock entry.
    """
    # 1. Create a stock to delete
    stock_data = {
        "ticker": "NVDA",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T13:00:00",
        "open": 500.0,
        "high": 510.0,
        "low": 498.0,
        "close": 508.0,
        "volume": 1200000,
    }
    create_response = await client.post("/robot/stocks/", json=stock_data)
    assert create_response.status_code == 200
    created_stock = create_response.json()
    stock_id = created_stock["id"]

    # 2. Send a DELETE request to the endpoint
    delete_response = await client.delete(f"/robot/stocks/{stock_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Stock deleted successfully"}

    # 3. Verify the stock is deleted
    get_response = await client.get(f"/stocks/{stock_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_all_stocks(client: AsyncClient):
    """
    Test case for deleting all stock entries.
    """
    # 1. Create multiple stocks
    stock_data_1 = {
        "ticker": "NVDA",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T13:00:00",
        "open": 500.0,
        "high": 510.0,
        "low": 498.0,
        "close": 508.0,
        "volume": 1200000,
    }
    stock_data_2 = {
        "ticker": "AAPL",
        "market": "NASDAQ",
        "currency": "USD",
        "time": "2025-08-13T14:00:00",
        "open": 150.0,
        "high": 152.0,
        "low": 149.0,
        "close": 151.0,
        "volume": 2000000,
    }
    await client.post("/robot/stocks/", json=stock_data_1)
    await asyncio.sleep(0)  # Yield control to the event loop
    await client.post("/robot/stocks/", json=stock_data_2)
    await asyncio.sleep(0)  # Yield control to the event loop

    # 2. Verify stocks exist
    get_all_response = await client.get("/robot/stocks/")  # Assuming a GET /stocks/ endpoint exists to get all stocks
    assert get_all_response.status_code == 200
    assert len(get_all_response.json()) == 2

    # 3. Send a DELETE request to delete all stocks
    delete_all_response = await client.delete("/robot/stocks/all")
    assert delete_all_response.status_code == 200
    assert "Successfully deleted 2 stocks" in delete_all_response.json()["message"]

    # 4. Verify all stocks are deleted
    get_all_response_after_delete = await client.get("/robot/stocks/")
    assert get_all_response_after_delete.status_code == 200
    assert len(get_all_response_after_delete.json()) == 0
