from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.device import Device as DeviceModel, DeviceStatus
from app.schemas.device import DeviceCreate, DeviceUpdate, Device as DeviceSchema

OFFLINE_THRESHOLD_SECONDS = 300

def calculate_status(last_seen: datetime | None) -> DeviceStatus:
    """Calculate device status based on last_seen timestamp."""
    if last_seen is None:
        return DeviceStatus.OFFLINE
    
    now = datetime.now(timezone.utc)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    diff = (now - last_seen).total_seconds()
    return DeviceStatus.ONLINE if diff <= OFFLINE_THRESHOLD_SECONDS else DeviceStatus.OFFLINE

def to_response(device: DeviceModel) -> DeviceSchema:
    """Convert DB model to response schema with calculated status."""
    return DeviceSchema(
        id=device.id,
        type=device.type,
        location=device.location,
        function=device.function,
        status=calculate_status(device.last_seen),
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
    return [to_response(d) for d in devices]

async def get_by_id(db: AsyncSession, device_id: int) -> DeviceSchema | None:
    """Get a device by ID."""
    device = await db.get(DeviceModel, device_id)
    return to_response(device) if device else None

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
    return to_response(device)

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
    return to_response(device)

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