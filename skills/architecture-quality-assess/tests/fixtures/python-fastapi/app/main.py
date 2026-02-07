"""Main FastAPI application entry point."""

from fastapi import FastAPI
from app.routers import users

app = FastAPI(title="FastAPI Test Fixture")

app.include_router(users.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to FastAPI"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
