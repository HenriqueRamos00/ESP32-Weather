import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config import settings
from app.models.api_key import ApiKey as ApiKeyModel
from app.schemas.api_key import ApiKeyCreate, ApiKeyWithSecret

API_KEY_HASH_SECRET = settings.API_KEY_HASH_SECRET

def hash_key(key: str) -> str:
    return hmac.new(
        API_KEY_HASH_SECRET.encode("utf-8"),
        key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def generate_key() -> str:
    """Generate a secure API key."""
    return f"sk_esp_{secrets.token_hex(24)}"

async def get_all(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> Sequence[ApiKeyModel]:
    """Get all API keys with pagination."""
    stmt = select(ApiKeyModel).offset(skip).limit(limit).order_by(ApiKeyModel.id.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_by_device_id(
    db: AsyncSession, 
    device_id: int
) -> Sequence[ApiKeyModel]:
    """Get all API keys for a device."""
    stmt = select(ApiKeyModel).where(ApiKeyModel.device_id == device_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_by_id(db: AsyncSession, key_id: int) -> ApiKeyModel | None:
    """Get an API key by ID."""
    return await db.get(ApiKeyModel, key_id)

async def get_by_key(db: AsyncSession, key: str) -> ApiKeyModel | None:
    """Get an API key by the key value."""
    key_hash = hash_key(key)
    stmt = select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create(db: AsyncSession, api_key_in: ApiKeyCreate) -> ApiKeyWithSecret:
    """Create a new API key."""
    raw_key = generate_key()
    api_key = ApiKeyModel(
        key_hash=hash_key(raw_key),
        name=api_key_in.name,
        device_id=api_key_in.device_id,
        is_active=True,
    )
    db.add(api_key)
    await db.flush()
    await db.refresh(api_key)

    # Construct response manually to include plaintext key
    return ApiKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        device_id=api_key.device_id,
        is_active=api_key.is_active,
        last_used=api_key.last_used,
        created_at=api_key.created_at,
        key=raw_key,
    )

async def revoke(db: AsyncSession, key_id: int) -> ApiKeyModel | None:
    """Revoke an API key."""
    api_key = await db.get(ApiKeyModel, key_id)
    if not api_key:
        return None
    
    api_key.is_active = False
    await db.flush()
    await db.refresh(api_key)
    return api_key

async def delete(db: AsyncSession, key_id: int) -> bool:
    """Delete an API key."""
    api_key = await db.get(ApiKeyModel, key_id)
    if not api_key:
        return False
    
    await db.delete(api_key)
    await db.flush()
    return True

async def update_last_used(db: AsyncSession, key_id: int) -> None:
    """Update the last_used timestamp."""
    api_key = await db.get(ApiKeyModel, key_id)
    if api_key:
        api_key.last_used = datetime.now(timezone.utc)
        await db.flush()

async def count(db: AsyncSession) -> int:
    """Count total API keys."""
    stmt = select(func.count()).select_from(ApiKeyModel)
    result = await db.execute(stmt)
    return result.scalar_one()

async def count_by_device(db: AsyncSession, device_id: int) -> int:
    """Count API keys for a device."""
    stmt = select(func.count()).select_from(ApiKeyModel).where(
        ApiKeyModel.device_id == device_id
    )
    result = await db.execute(stmt)
    return result.scalar_one()