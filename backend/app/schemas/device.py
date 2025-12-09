from datetime import datetime
from typing import Sequence
from pydantic import BaseModel, ConfigDict
from app.models.device import DeviceType, DeviceStatus, DeviceFunction


class DeviceBase(BaseModel):
    type: DeviceType
    location: str
    function: DeviceFunction

class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    type: DeviceType | None = None
    location: str | None = None
    function: str | None = None


class DeviceInDB(DeviceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_seen: datetime | None
    created_at: datetime
    updated_at: datetime


class Device(DeviceInDB):
    status: DeviceStatus
    pass


class DeviceList(BaseModel):
    devices: Sequence[Device]
    total: int