from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.backend.api import stock_api
from src.backend.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the application.
    Creates database tables on startup.
    """
    await create_db_and_tables()
    yield


app = FastAPI(
    title="Stock Playground API",
    description="API for a toy project to manage stock information.",
    version="0.1.0",
    lifespan=lifespan,
)

# Include the API router from stock_api.py
app.include_router(stock_api.router, tags=["Stocks"])


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Stock Playground API!"}
