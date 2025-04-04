from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from pathlib import Path
from .core.database import engine
from .api.v1.endpoints import objects, tables, functions, test_cases

# Create FastAPI app
app = FastAPI(
    title="Schema & Process Management API",
    description="API for managing Objects, Tables, Functions, and TestCases",
    version="1.0.0"
)

# Include routers
app.include_router(objects.router, prefix="/api/v1")
app.include_router(tables.router, prefix="/api/v1")
app.include_router(functions.router, prefix="/api/v1")
app.include_router(test_cases.router, prefix="/api/v1")

# Create tables on startup
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

# Basic root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Schema & Process Management API"}
