from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Float, DateTime, ForeignKey, Integer, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.device import Device


class WeatherReading(Base):
    __tablename__ = "weather_readings"
    __table_args__ = (
        Index("ix_weather_readings_device_recorded", "device_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Weather metrics
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)  # Celsius
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)  # Percentage 0-100
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)  # hPa
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)  # m/s
    rain_amount: Mapped[float | None] = mapped_column(Float, nullable=True)  # mm
    
    # Timestamps
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="weather_readings")