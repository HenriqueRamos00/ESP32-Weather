# scripts/init_settings.py
import asyncio
import sqlalchemy as sa

from app.core.config import settings as app_settings
from app.db.session import engine
from app.models.setting import Setting

# Default settings configuration
DEFAULT_SETTINGS = {
    "offline_threshold_seconds": {
        "value": "300",
        "description": "Number of seconds before a device is considered offline"
    },
    #"max_devices_per_user": {
    #    "value": "10",
    #    "description": "Maximum number of devices a user can register"
    #},
    #"data_retention_days": {
    #    "value": "90",
    #    "description": "Number of days to retain device data"
    #},
}

async def init_settings():
    """Initialize or update default settings."""
    async with engine.begin() as db:
        for key, data in DEFAULT_SETTINGS.items():
            # Check if setting exists
            result = await db.execute(
                sa.select(Setting).where(Setting.key == key)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Optionally update description if it changed
                if existing.description != data.get("description"):
                    await db.execute(
                        sa.update(Setting)
                        .where(Setting.key == key)
                        .values(description=data.get("description"))
                    )
                    print(f"✓ Setting updated: {key} (description)")
                else:
                    print(f"✓ Setting exists: {key} = {existing.value}")
            else:
                # Create new setting
                await db.execute(
                    sa.insert(Setting).values(
                        key=key,
                        value=data["value"],
                        description=data.get("description"),
                    )
                )
                print(f"✓ Setting created: {key} = {data['value']}")

if __name__ == "__main__":
    print("Initializing default settings...")
    asyncio.run(init_settings())
    print("✓ Settings initialization complete!")