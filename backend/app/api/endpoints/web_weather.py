from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from app.api.deps import AsyncSessionDep, AdminOrUserDep
from app.schemas.weather_reading import (
    WeatherReadingList,
    WeatherReadingWithLocation,
    LatestReadings,
    WeatherSummary,
    WeatherGranularity
)
from app.utils.weather_reading import DEFAULT_AGG_LOOKBACK
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
    limit: int = Query(100, ge=1, le=5000),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    granularity: WeatherGranularity | None = Query(
        None,
        description=(
            "Aggregate readings into time buckets. If omitted and auto_granularity=true, "
            "the API picks a granularity based on the date range."
        ),
    ),
    auto_granularity: bool = Query(
        False,
        description="If true, pick an appropriate granularity based on start_time/end_time.",
    ),
) -> Any:
    """
    Get all weather readings with pagination and optional time filtering.
    """
    # Aggregation mode: do bucketed aggregation at query-time and enforce max payload size.
    if granularity is not None or auto_granularity:
        if start_time is None or end_time is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time and end_time are required when using granularity/auto_granularity on this endpoint.",
            )
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time must be earlier than end_time.",
            )
        agg_readings, effective = await weather_service.get_aggregated_all(
            db,
            start_time=start_time,
            end_time=end_time,
            granularity=granularity,
            auto_granularity=auto_granularity,
            skip=skip,
            limit=limit,
        )
        return WeatherReadingList(
            readings=agg_readings,
            total=len(agg_readings),
            aggregated=True,
            granularity=effective,
        )
    
    # Raw mode
    raw_readings = await weather_service.get_all(
        db,
        skip=skip,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
    )
    total = await weather_service.count(db, start_time=start_time, end_time=end_time)
    
    return WeatherReadingList(readings=raw_readings, total=total)

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
    limit: int = Query(100, ge=1, le=5000),
    start_time: datetime | None = Query(None, description="Filter readings from this time"),
    end_time: datetime | None = Query(None, description="Filter readings until this time"),
    granularity: WeatherGranularity | None = Query(
        None,
        description=(
            "Aggregate readings into time buckets. If omitted and auto_granularity=true, "
            "the API picks a granularity based on the date range.")),
    auto_granularity: bool = Query(
        True,
        description="If true and granularity is not set, pick an appropriate granularity based on the date range.",),
) -> Any:
    """
    Get historical weather readings from a specific sensor.
    
    Supports pagination, time range filtering, and optional query-time aggregation.
    """
    # If aggregation is requested but no range is specified, default to last 24h.
    if (granularity is not None or auto_granularity) and (start_time is None and end_time is None):
        end_time = datetime.now(timezone.utc)
        start_time = end_time.replace()  # copy
        start_time = start_time - DEFAULT_AGG_LOOKBACK
    
    if granularity is not None or auto_granularity:
        if start_time is None or end_time is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time and end_time are required when using granularity/auto_granularity.",
            )
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time must be earlier than end_time.",
            )
        agg_readings, effective = await weather_service.get_aggregated_by_device(
            db,
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            granularity=granularity,
            auto_granularity=auto_granularity,
            skip=skip,
            limit=limit,
        )
        return WeatherReadingList(
            readings=agg_readings,
            total=len(agg_readings),
            aggregated=True,
            granularity=effective,
        )
    
    # Raw mode
    raw_readings = await weather_service.get_by_device(
        db,
        device_id,
        skip=skip,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
    )
    total = await weather_service.count(
        db, device_id=device_id, start_time=start_time, end_time=end_time
    )
    return WeatherReadingList(readings=raw_readings, total=total)

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