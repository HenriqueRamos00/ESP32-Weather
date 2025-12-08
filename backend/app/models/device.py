from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DeviceType(str, Enum):
    ESP32 = "ESP32"
    ESP8266 = "ESP8266"
    ESP32_S3 = "ESP32-S3"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[DeviceStatus] = mapped_column(
        SQLEnum(DeviceStatus), 
        default=DeviceStatus.OFFLINE,
        nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )