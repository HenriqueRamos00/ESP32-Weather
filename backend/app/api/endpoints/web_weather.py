from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from app.api.deps import AsyncSessionDep, AdminOrUserDep
from app.schemas.weather_reading import (
    WeatherReadingList,
    WeatherReadingWithLocation,
    LatestReadings,
    WeatherSummary,
)
import app.services.weather_reading as weather_service

router = APIRouter()

@router.get(
    "/display/latest",
    response_model=LatestReadings,
    summary="Get latest readings for display",
    description="Get the most recent reading from each sensor. Optimized for display boards.",
)
async def get_latest_for_display(
    db: AsyncSessionDep,
    _: AdminOrUserDep
) -> Any:
    """
    Get the latest weather reading from all sensor devices.
    
    Returns one reading per sensor with device location info.
    Optimized endpoint for display boards to show current conditions.
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
    _: AdminOrUserDep
) -> Any:
    """
    Get the latest weather reading from a specific sensor.
    """
    reading = await weather_service.get_latest_by_device(db, device_id)
    
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No readings found for device {device_id}",
        )
    
    # Load device relationship if not already loaded
    await db.refresh(reading, ["device"])
    
    return reading


@router.get(
    "/readings",
    response_model=WeatherReadingList,
    summary="Get all weather readings",
)
async def get_all_readings(
    db: AsyncSessionDep,
    _: AdminOrUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
) -> Any:
    """
    Get all weather readings with pagination and optional time filtering.
    """
    readings = await weather_service.get_all(
        db,
        skip=skip,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
    )
    
    total = await weather_service.count(
        db,
        start_time=start_time,
        end_time=end_time,
    )
    
    return WeatherReadingList(readings=readings, total=total)

@router.get(
    "/display/sensor/{device_id}/history",
    response_model=WeatherReadingList,
    summary="Get reading history for sensor",
)
async def get_sensor_history(
    device_id: int,
    db: AsyncSessionDep,
    _: AdminOrUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    start_time: datetime | None = Query(None, description="Filter readings from this time"),
    end_time: datetime | None = Query(None, description="Filter readings until this time"),
) -> Any:
    """
    Get historical weather readings from a specific sensor.
    
    Supports pagination and time range filtering.
    """
    readings = await weather_service.get_by_device(
        db, 
        device_id, 
        skip=skip, 
        limit=limit,
        start_time=start_time, 
        end_time=end_time,
    )
    
    total = await weather_service.count(
        db,
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
    )
    
    return WeatherReadingList(readings=readings, total=total)

@router.get(
    "/display/sensor/{device_id}/summary",
    response_model=WeatherSummary,
    summary="Get weather summary for sensor",
)
async def get_sensor_summary(
    device_id: int,
    db: AsyncSessionDep,
    _: AdminOrUserDep,
    hours: int = Query(24, ge=1, le=168, description="Hours to aggregate (1-168)"),
) -> Any:
    """
    Get aggregated weather summary for a sensor over specified hours.

    Includes min/max/avg temperature, average humidity and pressure.
    """
    try:
        return await weather_service.get_summary_by_device(db, device_id, hours)
    except weather_service.DeviceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except weather_service.NoReadingsFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )