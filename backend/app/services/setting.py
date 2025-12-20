from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.setting import Setting as SettingModel
from app.schemas.setting import SettingCreate, SettingUpdate, Setting as SettingSchema

async def get_all(db: AsyncSession) -> list[SettingSchema]:
    """Get all settings."""
    stmt = select(SettingModel)
    result = await db.execute(stmt)
    settings = result.scalars().all()
    return [SettingSchema.model_validate(s) for s in settings]

async def get_by_key(db: AsyncSession, key: str) -> SettingSchema | None:
    """Get a setting by key."""
    stmt = select(SettingModel).where(SettingModel.key == key)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()
    return SettingSchema.model_validate(setting) if setting else None

async def upsert(db: AsyncSession, key: str, setting_in: SettingUpdate) -> SettingSchema:
    """Create or update a setting."""
    stmt = select(SettingModel).where(SettingModel.key == key)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = setting_in.value
    else:
        setting = SettingModel(key=key, value=setting_in.value)
        db.add(setting)
    
    await db.flush()
    await db.refresh(setting)
    return SettingSchema.model_validate(setting)

async def initialize_defaults(db: AsyncSession) -> None:
    """Initialize default settings if they don't exist."""
    defaults = {
        "offline_threshold_seconds": {
            "value": "300",
            "description": "Number of seconds before a device is considered offline"
        }
    }
    
    for key, data in defaults.items():
        stmt = select(SettingModel).where(SettingModel.key == key)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            setting = SettingModel(
                key=key,
                value=data["value"],
                description=data.get("description")
            )
            db.add(setting)
    
    await db.commit()