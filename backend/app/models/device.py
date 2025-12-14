from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import String, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.api_key import ApiKey
    from app.models.weather_reading import WeatherReading

class DeviceType(str, Enum):
    ESP32 = "ESP32"
    ESP8266 = "ESP8266"
    ESP32_S3 = "ESP32-S3"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class DeviceFunction(str, Enum):
    SENSOR = "sensor"
    DISPLAY = "display"

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    function: Mapped[DeviceFunction] = mapped_column(SQLEnum(DeviceFunction), nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    api_keys: Mapped[List["ApiKey"]] = relationship(
        "ApiKey", 
        back_populates="device",
        cascade="all, delete-orphan"
    )

    weather_readings: Mapped[List["WeatherReading"]] = relationship(
        "WeatherReading",
        back_populates="device",
        cascade="all, delete-orphan"
    )