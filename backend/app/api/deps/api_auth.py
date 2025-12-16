from typing import Annotated
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.db.session import get_db
from app.models.api_key import ApiKey as ApiKeyModel
from app.models.device import Device as DeviceModel, DeviceFunction
import app.services.api_key as api_key_service

api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="API Key for ESP device authentication",
    auto_error=False
)


async def get_api_key(
    db: Annotated[AsyncSession, Depends(get_db)],
    api_key: Annotated[str | None, Security(api_key_header)],
) -> ApiKeyModel:
    """Validate API key from X-API-Key header."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    key_record = await api_key_service.get_by_key(db, api_key)
    
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has been revoked",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Update API key last_used after successful validation
    await api_key_service.update_last_used(db, key_record.id)
    
    return key_record


async def get_authenticated_device(
    db: Annotated[AsyncSession, Depends(get_db)],
    api_key: Annotated[ApiKeyModel, Depends(get_api_key)],
) -> DeviceModel:
    """Get device associated with API key and update last_seen."""
    device = await db.get(DeviceModel, api_key.device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device associated with API key not found",
        )
    
    # Update device last_seen after successful authentication
    device.last_seen = datetime.now(timezone.utc)
    await db.flush()
    
    return device


async def get_sensor_device(
    device: Annotated[DeviceModel, Depends(get_authenticated_device)],
) -> DeviceModel:
    """Validate the authenticated device is a sensor."""
    if device.function != DeviceFunction.SENSOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Device function is '{device.function.value}', expected 'sensor'",
        )
    return device


async def get_display_device(
    device: Annotated[DeviceModel, Depends(get_authenticated_device)],
) -> DeviceModel:
    """Validate the authenticated device is a display."""
    if device.function != DeviceFunction.DISPLAY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Device function is '{device.function.value}', expected 'display'",
        )
    return device

ApiKeyDep = Annotated[ApiKeyModel, Depends(get_api_key)]
AuthenticatedDeviceDep = Annotated[DeviceModel, Depends(get_authenticated_device)]
SensorDeviceDep = Annotated[DeviceModel, Depends(get_sensor_device)]
DisplayDeviceDep = Annotated[DeviceModel, Depends(get_display_device)]