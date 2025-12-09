from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.api.deps import AsyncSessionDep
from app.schemas.api_key import ApiKey, ApiKeyCreate, ApiKeyWithSecret, ApiKeyList
import app.services.api_key as key
import app.services.device as dvc

router = APIRouter()


@router.get("/", response_model=ApiKeyList)
async def get_api_keys(
    db: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all API keys."""
    api_keys = await key.get_all(db, skip=skip, limit=limit)
    total = await key.count(db)
    return {"api_keys": api_keys, "total": total}


@router.get("/device/{device_id}", response_model=ApiKeyList)
async def get_device_api_keys(
    device_id: int,
    db: AsyncSessionDep,
) -> Any:
    """Get all API keys for a specific device."""
    device = await dvc.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    
    api_keys = await key.get_by_device_id(db, device_id)
    total = await key.count_by_device(db, device_id)
    return {"api_keys": api_keys, "total": total}


@router.post("/", response_model=ApiKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(api_key_in: ApiKeyCreate, db: AsyncSessionDep) -> Any:
    """Create a new API key. The key value is only returned once."""
    device = await dvc.get_by_id(db, api_key_in.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    
    return await key.create(db, api_key_in)


@router.post("/{key_id}/revoke", response_model=ApiKey)
async def revoke_api_key(key_id: int, db: AsyncSessionDep) -> Any:
    """Revoke an API key."""
    api_key = await key.revoke(db, key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(key_id: int, db: AsyncSessionDep) -> None:
    """Delete an API key."""
    success = await key.delete(db, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )