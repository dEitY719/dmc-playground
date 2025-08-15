from collections.abc import AsyncGenerator  # Added for lifespan return type
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.backend.api import stock_api
from src.backend.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # Added return type
    """
    Lifespan manager for the application.
    Creates database tables on startup.
    """
    await create_db_and_tables()
    yield


fastapi_app = FastAPI(  # Renamed app to fastapi_app
    title="Stock Playground API",
    description="API for a toy project to manage stock information.",
    version="0.1.0",
    lifespan=lifespan,
)

# Include the API router from stock_api.py
fastapi_app.include_router(stock_api.router, tags=["Stocks"])  # Used fastapi_app


@fastapi_app.get("/", tags=["Root"])  # Used fastapi_app
def read_root() -> dict[str, str]:  # Added return type
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Stock Playground API!"}
