from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import devices, esp32_weather, health, api_keys, web_weather
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(
    devices.router,
    prefix=f"{settings.API_V1_STR}/devices",
    tags=["devices"],
)
app.include_router(
    api_keys.router, 
    prefix=f"{settings.API_V1_STR}/api-keys", 
    tags=["api-keys"]
)
app.include_router(
    esp32_weather.router,
    prefix=f"{settings.API_V1_STR}/esp32", 
    tags=["esp32-weather"]
)
app.include_router(
    web_weather.router,
    prefix=f"{settings.API_V1_STR}/weather",
    tags=["web-weather"]
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Device Management API"}