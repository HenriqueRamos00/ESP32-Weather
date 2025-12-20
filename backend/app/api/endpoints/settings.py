from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.setting import Setting, SettingUpdate
from app.api.deps import AsyncSessionDep, AdminDep
import app.services.setting as sett

router = APIRouter()

@router.get("/", response_model=list[Setting])
async def get_settings(
    db: AsyncSessionDep,
    _: AdminDep
) -> Any:
    """Get all settings (admin only)."""
    return await sett.get_all(db)

@router.get("/{key}", response_model=Setting)
async def get_setting(
    key: str,
    db: AsyncSessionDep,
    _: AdminDep
) -> Any:
    """Get a specific setting (admin only)."""
    setting = await sett.get_by_key(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/{key}", response_model=Setting)
async def update_setting(
    key: str,
    setting_in: SettingUpdate,
    db: AsyncSessionDep,
    _: AdminDep
) -> Any:
    """Update a setting (admin only)."""
    setting = await sett.upsert(db, key, setting_in)
    await db.commit()
    return setting