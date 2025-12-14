# schemas/weather_reading.py
from datetime import datetime
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


class WeatherReadingList(BaseModel):
    """Paginated list of weather readings."""
    readings: Sequence[WeatherReading]
    total: int


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