from collections.abc import AsyncGenerator  # Added for lifespan return type
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.backend.__version__ import __version__
from src.backend.api.robot_stock_api import stockbot_router
from src.backend.api.stock_api import router as stock_router
from src.backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # Added return type
    """
    Lifespan manager for the application.
    Creates database tables on startup.
    """
    await init_db()
    yield


app = FastAPI(  # Renamed app to fastapi_app
    title="Stock Playground API",
    description="API for a toy project to manage stock information.",
    version=__version__,
    lifespan=lifespan,
)

# Include the API router from stock_api.py
app.include_router(stockbot_router, prefix="/robot")
app.include_router(stock_router)


@app.get("/", tags=["Root"])  # Used fastapi_app
def read_root() -> dict[str, str]:  # Added return type
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Stock Playground API!"}
