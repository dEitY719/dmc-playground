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
