from datetime import datetime, timezone, timedelta
from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import joinedload
from app.models.weather_reading import WeatherReading as WeatherReadingModel
from app.models.device import Device as DeviceModel, DeviceFunction
from app.schemas.weather_reading import (
    WeatherReadingCreate, 
    WeatherSummary,
    WeatherReading as WeatherReadingSchema,
    WeatherReadingWithLocation
)

class DeviceNotFoundError(Exception):
    """Raised when the device does not exist."""
    pass


class NoReadingsFoundError(Exception):
    """Raised when there are no readings for the device in the given period."""
    pass

def to_response(reading: WeatherReadingModel) -> WeatherReadingSchema:
    """Convert DB model to response schema."""
    return WeatherReadingSchema(
        id=reading.id,
        device_id=reading.device_id,
        temperature=reading.temperature,
        humidity=reading.humidity,
        pressure=reading.pressure,
        wind_speed=reading.wind_speed,
        rain_amount=reading.rain_amount,
        recorded_at=reading.recorded_at,
        created_at=reading.created_at,
    )

def to_response_with_loc(reading: WeatherReadingModel) -> WeatherReadingWithLocation:
    """Convert DB model to response schema with location."""
    return WeatherReadingWithLocation(
        id=reading.id,
        device_id=reading.device_id,
        device_location=reading.device.location,
        temperature=reading.temperature,
        humidity=reading.humidity,
        pressure=reading.pressure,
        wind_speed=reading.wind_speed,
        rain_amount=reading.rain_amount,
        recorded_at=reading.recorded_at,
        created_at=reading.created_at,
    )

async def create(
    db: AsyncSession,
    device_id: int,
    reading_in: WeatherReadingCreate,
) -> WeatherReadingSchema:
    """Create a new weather reading from sensor data."""
    reading = WeatherReadingModel(
        device_id=device_id,
        temperature=reading_in.temperature,
        humidity=reading_in.humidity,
        pressure=reading_in.pressure,
        wind_speed=reading_in.wind_speed,
        rain_amount=reading_in.rain_amount,
        recorded_at=reading_in.recorded_at or datetime.now(timezone.utc),
    )
    db.add(reading)
    await db.flush()
    await db.refresh(reading)
    return to_response(reading)


async def get_by_id(
    db: AsyncSession, 
    reading_id: int,
) -> WeatherReadingSchema | None:
    """Get a weather reading by ID."""
    result = await db.get(WeatherReadingModel, reading_id)
    return to_response(result) if result else None


async def get_latest_by_device(
    db: AsyncSession,
    device_id: int,
) -> WeatherReadingWithLocation | None:
    """Get the most recent weather reading for a specific device."""
    stmt = (
        select(WeatherReadingModel)
        .where(WeatherReadingModel.device_id == device_id)
        .order_by(desc(WeatherReadingModel.recorded_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    reading = result.scalar_one_or_none()
    return to_response_with_loc(reading) if reading else None


async def get_latest_from_all_sensors(
    db: AsyncSession,
) -> list[WeatherReadingWithLocation]:
    """
    Get the latest weather reading from each sensor device.
    Uses a window function for efficient retrieval.
    """
    # Subquery to get max recorded_at for each device
    subquery = (
        select(
            WeatherReadingModel.device_id,
            func.max(WeatherReadingModel.recorded_at).label("max_recorded")
        )
        .group_by(WeatherReadingModel.device_id)
        .subquery()
    )
    
    # Main query joining with subquery
    stmt = (
        select(WeatherReadingModel)
        .join(
            subquery,
            and_(
                WeatherReadingModel.device_id == subquery.c.device_id,
                WeatherReadingModel.recorded_at == subquery.c.max_recorded
            )
        )
        .options(joinedload(WeatherReadingModel.device))
        .order_by(WeatherReadingModel.device_id)
    )
    
    result = await db.execute(stmt)
    readings = result.scalars().unique().all()
    
    return [to_response_with_loc(r) for r in readings]


async def get_by_device(
    db: AsyncSession,
    device_id: int,
    skip: int = 0,
    limit: int = 100,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[WeatherReadingSchema]:
    """Get weather readings for a device with optional time range filter."""
    stmt = (
        select(WeatherReadingModel)
        .where(WeatherReadingModel.device_id == device_id)
    )
    
    if start_time:
        stmt = stmt.where(WeatherReadingModel.recorded_at >= start_time)
    if end_time:
        stmt = stmt.where(WeatherReadingModel.recorded_at <= end_time)
    
    stmt = (
        stmt
        .order_by(desc(WeatherReadingModel.recorded_at))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    readings = result.scalars().all()
    return [to_response(r) for r in readings]


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    device_ids: list[int] | None = None,
) -> list[WeatherReadingSchema]:
    """Get all weather readings with optional filters."""
    stmt = select(WeatherReadingModel)
    
    if device_ids:
        stmt = stmt.where(WeatherReadingModel.device_id.in_(device_ids))
    if start_time:
        stmt = stmt.where(WeatherReadingModel.recorded_at >= start_time)
    if end_time:
        stmt = stmt.where(WeatherReadingModel.recorded_at <= end_time)
    
    stmt = (
        stmt
        .order_by(desc(WeatherReadingModel.recorded_at))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    readings = result.scalars().all()
    return [to_response(r) for r in readings]


async def get_summary_by_device(
    db: AsyncSession,
    device_id: int,
    hours: int = 24,
) -> WeatherSummary:
    """Get aggregated weather summary for a device over specified hours."""
    # 1) Load device (for location and existence check)
    device = await db.get(DeviceModel, device_id)
    if not device:
        raise DeviceNotFoundError(f"Device {device_id} not found")

    # 2) Aggregate readings
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    stmt = (
        select(
            func.avg(WeatherReadingModel.temperature).label("avg_temperature"),
            func.min(WeatherReadingModel.temperature).label("min_temperature"),
            func.max(WeatherReadingModel.temperature).label("max_temperature"),
            func.avg(WeatherReadingModel.humidity).label("avg_humidity"),
            func.avg(WeatherReadingModel.pressure).label("avg_pressure"),
            func.count(WeatherReadingModel.id).label("reading_count"),
            func.min(WeatherReadingModel.recorded_at).label("period_start"),
            func.max(WeatherReadingModel.recorded_at).label("period_end"),
        )
        .where(
            and_(
                WeatherReadingModel.device_id == device_id,
                WeatherReadingModel.recorded_at >= cutoff,
            )
        )
    )

    result = await db.execute(stmt)
    row = result.one_or_none()

    if not row or row.reading_count == 0:
        raise NoReadingsFoundError(
            f"No readings found for device {device_id} in the last {hours} hours"
        )

    # 3) Build and return WeatherSummary here (service layer)
    return WeatherSummary(
        device_id=device_id,
        device_location=device.location,
        avg_temperature=row.avg_temperature,
        min_temperature=row.min_temperature,
        max_temperature=row.max_temperature,
        avg_humidity=row.avg_humidity,
        avg_pressure=row.avg_pressure,
        reading_count=row.reading_count,
        period_start=row.period_start,
        period_end=row.period_end,
    )


async def count(
    db: AsyncSession,
    device_id: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> int:
    """Count weather readings with optional filters."""
    stmt = select(func.count()).select_from(WeatherReadingModel)
    
    if device_id:
        stmt = stmt.where(WeatherReadingModel.device_id == device_id)
    if start_time:
        stmt = stmt.where(WeatherReadingModel.recorded_at >= start_time)
    if end_time:
        stmt = stmt.where(WeatherReadingModel.recorded_at <= end_time)
    
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_old_readings(
    db: AsyncSession,
    days: int = 30,
) -> int:
    """Delete readings older than specified number of days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    stmt = select(WeatherReadingModel).where(
        WeatherReadingModel.recorded_at < cutoff
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()
    deleted_count = len(readings)
    
    for reading in readings:
        await db.delete(reading)
    
    await db.flush()
    return deleted_count


async def get_sensor_devices(db: AsyncSession) -> Sequence[DeviceModel]:
    """Get all devices configured as sensors."""
    stmt = (
        select(DeviceModel)
        .where(DeviceModel.function == DeviceFunction.SENSOR)
        .order_by(DeviceModel.id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()