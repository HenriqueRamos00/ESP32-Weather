from datetime import datetime, timedelta
from typing import Any

from click import DateTime
from sqlalchemy import ColumnElement, func

from app.models.weather_reading import WeatherReading as WeatherReadingModel
from app.schemas.weather_reading import (
    WeatherGranularity,
    WeatherReadingAggregate,
    WeatherReading as WeatherReadingSchema,
    WeatherReadingWithLocation
)

# ---- Aggregation controls (payload protection) ----
MAX_SERIES_POINTS = 2000
DEFAULT_AGG_LOOKBACK = timedelta(hours=24)

_GRANULARITY_TO_SECONDS: dict[WeatherGranularity, int] = {
    WeatherGranularity.minute: 60,
    WeatherGranularity.five_min: 5 * 60,
    WeatherGranularity.fifteen_min: 15 * 60,
    WeatherGranularity.hour: 60 * 60,
    WeatherGranularity.six_hour: 6 * 60 * 60,
    WeatherGranularity.day: 24 * 60 * 60,
}

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

def pick_supported_bucket_seconds(required_seconds: int) -> tuple[WeatherGranularity, int]:
    # Pick the smallest supported granularity >= required_seconds
    for g, sec in sorted(_GRANULARITY_TO_SECONDS.items(), key=lambda kv: kv[1]):
        if sec >= required_seconds:
            return g, sec
    return WeatherGranularity.day, _GRANULARITY_TO_SECONDS[WeatherGranularity.day]

def auto_granularity_seconds(start_time: datetime, end_time: datetime) -> tuple[WeatherGranularity, int]:
    """
    Pick a default granularity based on range, then ensure it doesn't exceed MAX_SERIES_POINTS.
    """
    range_seconds = int((end_time - start_time).total_seconds())
    if range_seconds <= 0:
        return WeatherGranularity.minute, 60

    # Base heuristic
    if range_seconds <= 6 * 3600:
        base = WeatherGranularity.minute
    elif range_seconds <= 2 * 86400:
        base = WeatherGranularity.five_min
    elif range_seconds <= 7 * 86400:
        base = WeatherGranularity.fifteen_min
    elif range_seconds <= 31 * 86400:
        base = WeatherGranularity.hour
    elif range_seconds <= 180 * 86400:
        base = WeatherGranularity.six_hour
    else:
        base = WeatherGranularity.day

    base_seconds = _GRANULARITY_TO_SECONDS[base]

    # Enforce max points: ceil(range / bucket) <= MAX_SERIES_POINTS
    min_bucket = (range_seconds + MAX_SERIES_POINTS - 1) // MAX_SERIES_POINTS
    required = max(base_seconds, min_bucket)
    return pick_supported_bucket_seconds(required)

def effective_granularity(
    start_time: datetime,
    end_time: datetime,
    granularity: WeatherGranularity | None,
    auto_granularity: bool,
) -> tuple[WeatherGranularity, int]:
    if granularity is not None:
        bucket_seconds = _GRANULARITY_TO_SECONDS[granularity]
        # validate size if caller explicitly asked for a specific bucket
        range_seconds = int((end_time - start_time).total_seconds())
        if range_seconds > 0:
            points = (range_seconds + bucket_seconds - 1) // bucket_seconds
            if points > MAX_SERIES_POINTS:
                raise ValueError(
                    f"Requested granularity would return ~{points} points (> {MAX_SERIES_POINTS}). "
                    "Increase granularity or reduce the date range."
                )
        return granularity, bucket_seconds

    if auto_granularity:
        return auto_granularity_seconds(start_time, end_time)

    return WeatherGranularity.hour, _GRANULARITY_TO_SECONDS[WeatherGranularity.hour]

def bucket_expr(bucket_seconds: int) -> ColumnElement[DateTime]:
    """
    Bucket expression.
    """
    # Default (Postgres-compatible)
    return func.to_timestamp(
        func.floor(func.extract("epoch", WeatherReadingModel.recorded_at) / bucket_seconds)
        * bucket_seconds
    )

def row_to_aggregate(row: Any, device_id: int | None = None) -> WeatherReadingAggregate:
    return WeatherReadingAggregate(
        device_id=device_id,
        recorded_at=row.bucket,
        temperature=row.temperature,
        humidity=row.humidity,
        pressure=row.pressure,
        wind_speed=row.wind_speed,
        rain_amount=row.rain_amount,
        reading_count=row.reading_count,
    )