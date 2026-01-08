from datetime import datetime
from enum import Enum
from typing import Sequence
from pydantic import BaseModel, ConfigDict, Field


class WeatherReadingBase(BaseModel):
    """Base schema with common weather metrics."""
    temperature: float | None = Field(
        None, ge=-20, le=60, description="Temperature in Celsius"
    )
    humidity: float | None = Field(
        None, ge=0, le=100, description="Relative humidity percentage"
    )
    pressure: float | None = Field(
        None, ge=300, le=1500, description="Atmospheric pressure in hPa"
    )
    wind_speed: float | None = Field(
        None, ge=0, description="Wind speed in m/s"
    )
    rain_amount: float | None = Field(
        None, ge=0, description="Rain amount in mm"
    )

class WeatherGranularity(str, Enum):
    """
    Supported aggregation bucket sizes.
    """
    minute = "minute"
    five_min = "5min"
    fifteen_min = "15min"
    hour = "hour"
    six_hour = "6hour"
    day = "day"

class WeatherReadingCreate(WeatherReadingBase):
    """Schema for creating a weather reading from sensor."""
    recorded_at: datetime | None = Field(
        None, description="Timestamp of recording (defaults to server time)"
    )


class WeatherReadingInDB(WeatherReadingBase):
    """Schema representing weather reading in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_id: int
    recorded_at: datetime
    created_at: datetime


class WeatherReading(WeatherReadingInDB):
    """Response schema for weather reading."""
    pass


class WeatherReadingWithLocation(WeatherReading):
    """Weather reading with device location info for displays."""
    device_location: str

class WeatherReadingAggregate(WeatherReadingBase):
    """
    Query-time aggregated reading (bucketed).
    """
    device_id: int | None = None
    recorded_at: datetime
    reading_count: int = Field(..., ge=0)


class WeatherReadingList(BaseModel):
    """Paginated list of weather readings."""
    readings: Sequence[WeatherReading | WeatherReadingAggregate]
    total: int
    aggregated: bool = False
    granularity: WeatherGranularity | None = None


class LatestReadings(BaseModel):
    """Latest readings from all sensors for display boards."""
    readings: Sequence[WeatherReadingWithLocation]
    fetched_at: datetime


class WeatherSummary(BaseModel):
    """Aggregated weather summary."""
    device_id: int
    device_location: str
    avg_temperature: float | None
    min_temperature: float | None
    max_temperature: float | None
    avg_humidity: float | None
    avg_pressure: float | None
    reading_count: int
    period_start: datetime
    period_end: datetime