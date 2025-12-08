from datetime import datetime
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.device import Device as DeviceModel
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceService:
    @staticmethod
    async def get_all(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[DeviceModel]:
        """Get all devices with pagination."""
        stmt = select(DeviceModel).offset(skip).limit(limit).order_by(DeviceModel.id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, device_id: int) -> DeviceModel | None:
        """Get a device by ID."""
        return await db.get(DeviceModel, device_id)

    @staticmethod
    async def create(db: AsyncSession, device_in: DeviceCreate) -> DeviceModel:
        """Create a new device."""
        device = DeviceModel(
            type=device_in.type,
            location=device_in.location,
            status=device_in.status,
            last_seen=datetime.utcnow(),
        )
        db.add(device)
        await db.flush()
        await db.refresh(device)
        return device

    @staticmethod
    async def update(
        db: AsyncSession, 
        device_id: int, 
        device_in: DeviceUpdate
    ) -> DeviceModel | None:
        """Update a device."""
        device = await db.get(DeviceModel, device_id)
        if not device:
            return None
        
        update_data = device_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)
        
        device.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(device)
        return device

    @staticmethod
    async def delete(db: AsyncSession, device_id: int) -> bool:
        """Delete a device."""
        device = await db.get(DeviceModel, device_id)
        if not device:
            return False
        
        await db.delete(device)
        await db.flush()
        return True

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """Count total devices."""
        stmt = select(func.count()).select_from(DeviceModel)
        result = await db.execute(stmt)
        return result.scalar_one()