from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import (devices, esp32_weather, 
                               health, api_keys, web_weather,
                               auth, users, settings as settings_router)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url
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
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)
app.include_router(
    settings_router.router,
    prefix=f"{settings.API_V1_STR}/settings",
    tags=["settings"]
)