from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from app.api.deps import AsyncSessionDep, SensorDeviceDep, DisplayDeviceDep
from app.schemas.weather_reading import (
    WeatherReading,
    WeatherReadingCreate,
    WeatherReadingWithLocation,
    LatestReadings,
)
import app.services.weather_reading as weather_service

router = APIRouter()

@router.post(
    "/readings",
    response_model=WeatherReading,
    status_code=status.HTTP_201_CREATED,
    summary="Submit weather reading",
    description="Submit a new weather reading from a sensor board. Requires sensor device API key.",
)
async def submit_reading(
    reading_in: WeatherReadingCreate,
    db: AsyncSessionDep,
    device: SensorDeviceDep,
) -> Any:
    """
    Submit a weather reading from a sensor ESP board.
    
    - **temperature**: Temperature in Celsius (-100 to 100)
    - **humidity**: Relative humidity percentage (0-100)
    - **pressure**: Atmospheric pressure in hPa (300-1100)
    - **wind_speed**: Wind speed in m/s
    - **rain_amount**: Rain amount in mm
    - **recorded_at**: Optional timestamp (defaults to server time)
    
    Requires X-API-Key header with a valid sensor device API key.
    """
    reading = await weather_service.create(db, device.id, reading_in)
    return reading


# ============== DISPLAY ENDPOINTS ==============

@router.get(
    "/display/latest",
    response_model=LatestReadings,
    summary="Get latest readings for display",
    description="Get the most recent reading from each sensor. Optimized for display boards.",
)
async def get_latest_for_display(
    db: AsyncSessionDep,
    device: DisplayDeviceDep,
) -> Any:
    """
    Get the latest weather reading from all sensor devices.
    
    Returns one reading per sensor with device location info.
    Optimized endpoint for display boards to show current conditions.
    
    Requires X-API-Key header with a valid display device API key.
    """
    return LatestReadings(
        readings=await weather_service.get_latest_from_all_sensors(db),
        fetched_at=datetime.now(timezone.utc),
    )


@router.get(
    "/display/sensor/{device_id}/latest",
    response_model=WeatherReadingWithLocation,
    summary="Get latest reading from specific sensor",
)
async def get_sensor_latest_for_display(
    device_id: int,
    db: AsyncSessionDep,
    _device: DisplayDeviceDep,
) -> Any:
    """
    Get the latest weather reading from a specific sensor.
    
    Requires X-API-Key header with a valid display device API key.
    """
    reading = await weather_service.get_latest_by_device(db, device_id)
    
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No readings found for device {device_id}",
        )
    
    return reading
