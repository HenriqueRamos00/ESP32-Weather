from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.api.deps import AsyncSessionDep
from app.schemas.device import Device, DeviceCreate, DeviceUpdate, DeviceList
from app.services.device import DeviceService

router = APIRouter()


@router.get("/", response_model=DeviceList)
async def get_devices(
    db: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all devices."""
    devices = await DeviceService.get_all(db, skip=skip, limit=limit)
    total = await DeviceService.count(db)
    return {"devices": devices, "total": total}


@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: int, db: AsyncSessionDep) -> Any:
    """Get device by ID."""
    device = await DeviceService.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    return device


@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
async def create_device(device_in: DeviceCreate, db: AsyncSessionDep) -> Any:
    """Create new device."""
    return await DeviceService.create(db, device_in)


@router.put("/{device_id}", response_model=Device)
async def update_device(
    device_id: int,
    device_in: DeviceUpdate,
    db: AsyncSessionDep,
) -> Any:
    """Update device."""
    device = await DeviceService.update(db, device_id, device_in)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: int, db: AsyncSessionDep) -> None:
    """Delete device."""
    success = await DeviceService.delete(db, device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )