from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.device import Device as DeviceModel, DeviceStatus
from app.models.setting import Setting as SettingModel
from app.schemas.device import DeviceCreate, DeviceUpdate, Device as DeviceSchema

DEFAULT_OFFLINE_THRESHOLD_SECONDS = 300

async def get_offline_threshold(db: AsyncSession) -> int:
    """Get the offline threshold from settings or return default."""
    stmt = select(SettingModel).where(SettingModel.key == "offline_threshold_seconds")
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()
    
    if setting:
        try:
            return int(setting.value)
        except ValueError:
            return DEFAULT_OFFLINE_THRESHOLD_SECONDS
    return DEFAULT_OFFLINE_THRESHOLD_SECONDS

async def calculate_status(db: AsyncSession, last_seen: datetime | None) -> DeviceStatus:
    """Calculate device status based on last_seen timestamp."""
    if last_seen is None:
        return DeviceStatus.OFFLINE
    
    threshold = await get_offline_threshold(db)
    now = datetime.now(timezone.utc)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    diff = (now - last_seen).total_seconds()
    return DeviceStatus.ONLINE if diff <= threshold else DeviceStatus.OFFLINE

async def to_response(db: AsyncSession, device: DeviceModel) -> DeviceSchema:
    """Convert DB model to response schema with calculated status."""
    return DeviceSchema(
        id=device.id,
        type=device.type,
        location=device.location,
        function=device.function,
        status=await calculate_status(db, device.last_seen),
        last_seen=device.last_seen,
        created_at=device.created_at,
        updated_at=device.updated_at,
    )

async def get_all(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> list[DeviceSchema]:
    """Get all devices with pagination."""
    stmt = select(DeviceModel).offset(skip).limit(limit).order_by(DeviceModel.id)
    result = await db.execute(stmt)
    devices = result.scalars().all()
    return [await to_response(db, d) for d in devices]

async def get_by_id(db: AsyncSession, device_id: int) -> DeviceSchema | None:
    """Get a device by ID."""
    device = await db.get(DeviceModel, device_id)
    return await to_response(db, device) if device else None

async def create(db: AsyncSession, device_in: DeviceCreate) -> DeviceSchema:
    """Create a new device."""
    device = DeviceModel(
        type=device_in.type,
        location=device_in.location,
        function=device_in.function,
    )
    db.add(device)
    await db.flush()
    await db.refresh(device)
    return await to_response(db, device)

async def update(
    db: AsyncSession, 
    device_id: int, 
    device_in: DeviceUpdate
) -> DeviceSchema | None:
    """Update a device."""
    device = await db.get(DeviceModel, device_id)
    if not device:
        return None
    
    update_data = device_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    await db.flush()
    await db.refresh(device)
    return await to_response(db, device)

async def update_last_seen(db: AsyncSession, device_id: int) -> DeviceModel | None:
    """Update the last_seen timestamp when device communicates."""
    device = await db.get(DeviceModel, device_id)
    if not device:
        return None
    
    device.last_seen = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(device)
    return device

async def delete(db: AsyncSession, device_id: int) -> bool:
    """Delete a device."""
    device = await db.get(DeviceModel, device_id)
    if not device:
        return False
    
    await db.delete(device)
    await db.flush()
    return True

async def count(db: AsyncSession) -> int:
    """Count total devices."""
    stmt = select(func.count()).select_from(DeviceModel)
    result = await db.execute(stmt)
    return result.scalar_one()