from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from db import database  # ← import the `Database` instance
from contextlib import asynccontextmanager




@asynccontextmanager
async def lifespan(app:FastAPI):
    # Connect to the DB on startup
    await database.connect()
    yield
    # Disconnect on shutdown
    await database.disconnect()
    
app = FastAPI(title="Budget Maintenance BaaS",lifespan=lifespan)


@app.get("/",summary="Home")
async def home():
    return JSONResponse(content={"message":"Hi you are welcome to budget maintenance API"})

@app.get("/health",summary="Health Check")
async def healthcheck():
    return JSONResponse(content={"status":"ok","message":"API is healthy"})

