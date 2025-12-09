import secrets
from datetime import datetime
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.api_key import ApiKey as ApiKeyModel
from app.schemas.api_key import ApiKeyCreate


class ApiKeyService:
    @staticmethod
    def generate_key() -> str:
        """Generate a secure API key."""
        return f"sk_esp_{secrets.token_hex(24)}"

    @staticmethod
    async def get_all(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[ApiKeyModel]:
        """Get all API keys with pagination."""
        stmt = select(ApiKeyModel).offset(skip).limit(limit).order_by(ApiKeyModel.id.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_device_id(
        db: AsyncSession, 
        device_id: int
    ) -> Sequence[ApiKeyModel]:
        """Get all API keys for a device."""
        stmt = select(ApiKeyModel).where(ApiKeyModel.device_id == device_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, key_id: int) -> ApiKeyModel | None:
        """Get an API key by ID."""
        return await db.get(ApiKeyModel, key_id)

    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> ApiKeyModel | None:
        """Get an API key by the key value."""
        stmt = select(ApiKeyModel).where(ApiKeyModel.key == key)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, api_key_in: ApiKeyCreate) -> ApiKeyModel:
        """Create a new API key."""
        api_key = ApiKeyModel(
            key=ApiKeyService.generate_key(),
            name=api_key_in.name,
            device_id=api_key_in.device_id,
            is_active=True,
        )
        db.add(api_key)
        await db.flush()
        await db.refresh(api_key)
        return api_key

    @staticmethod
    async def revoke(db: AsyncSession, key_id: int) -> ApiKeyModel | None:
        """Revoke an API key."""
        api_key = await db.get(ApiKeyModel, key_id)
        if not api_key:
            return None
        
        api_key.is_active = False
        await db.flush()
        await db.refresh(api_key)
        return api_key

    @staticmethod
    async def delete(db: AsyncSession, key_id: int) -> bool:
        """Delete an API key."""
        api_key = await db.get(ApiKeyModel, key_id)
        if not api_key:
            return False
        
        await db.delete(api_key)
        await db.flush()
        return True

    @staticmethod
    async def update_last_used(db: AsyncSession, key_id: int) -> None:
        """Update the last_used timestamp."""
        api_key = await db.get(ApiKeyModel, key_id)
        if api_key:
            api_key.last_used = datetime.utcnow()
            await db.flush()

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """Count total API keys."""
        stmt = select(func.count()).select_from(ApiKeyModel)
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def count_by_device(db: AsyncSession, device_id: int) -> int:
        """Count API keys for a device."""
        stmt = select(func.count()).select_from(ApiKeyModel).where(
            ApiKeyModel.device_id == device_id
        )
        result = await db.execute(stmt)
        return result.scalar_one()